from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
import openai
import os
import json
import re
from matcher import match_studies
from utils import format_matches_for_gpt
from push_to_monday import push_to_monday
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """You are a clinical trial assistant named Hey Trial. Your job is to collect the following info one-by-one in a conversational tone:
- Name
- Email Address
- Phone Number
- Are you the person with autism, or are you filling this out on their behalf?
- Date of birth of the person with autism (please use formats like “January 19, 2020” or “19 Jan 2020”)
- City, State and Zipcode
- Can you receive text messages about studies?
- Has the individual been officially diagnosed with Autism Spectrum Disorder (ASD)?
- At what age was the diagnosis made?
- Is the individual verbal or non-verbal?
- Are they currently taking any medications for ASD or related conditions?
- What medications are they taking?
- Do they have any co-occurring conditions? (e.g., ADHD, anxiety, epilepsy)
- Are there any mobility limitations?
- Are they currently in school or a program?
- Are they open to in-person visits or only remote studies?
- Are you only interested in pediatric/adult studies?
- Are there any specific goals for participating (e.g., access to therapy, contributing to research)?

Ask one question at a time in a friendly tone. Use previous answers to skip ahead. Once all answers are collected, return only this dictionary:

{
  "name": ..., 
  "email": ..., 
  "phone": ..., 
  "relation": ..., 
  "dob": ..., 
  "location": ..., 
  "text_opt_in": ..., 
  "diagnosis": ..., 
  "diagnosis_age": ..., 
  "verbal": ..., 
  "medications": ..., 
  "medication_names": ..., 
  "co_conditions": ..., 
  "mobility": ..., 
  "school_program": ..., 
  "visit_type": ..., 
  "study_age_focus": ..., 
  "study_goals": ...
}

Say nothing else in that message. Do not match studies or explain yet."""

chat_histories = {}

def calculate_age(dob_str):
    """
    Attempt to parse multiple common date formats and compute age in years.
    """
    dob = None
    # Try full month name, e.g. "January 19, 2020"
    for fmt in ("%B %d, %Y", "%d %B %Y", "%d %b %Y"):
        try:
            dob = datetime.strptime(dob_str, fmt)
            break
        except:
            continue
    if not dob:
        # As a last resort, try ISO-like parse (YYYY-MM-DD)
        try:
            dob = datetime.fromisoformat(dob_str)
        except:
            return None
    today = datetime.today()
    # Age in years, accounting for month/day
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

@app.post("/chat")
async def chat_handler(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "default")
    user_input = body.get("message")

    if session_id not in chat_histories:
        chat_histories[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    chat_histories[session_id].append({"role": "user", "content": user_input})

    # 1) Collect participant info
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_histories[session_id],
        temperature=0.5
    )
    gpt_message = response.choices[0].message["content"]
    chat_histories[session_id].append({"role": "assistant", "content": gpt_message})

    # 2) If GPT returned the JSON dict, process studies
    match = re.search(r'{[\s\S]*}', gpt_message)
    if match:
        try:
            participant_data = json.loads(match.group())
            # Calculate age from the collected DOB
            participant_data["age"] = calculate_age(participant_data.get("dob", ""))

            # Push to Monday.com
            push_to_monday(participant_data)

            # Load and match studies
            with open("indexed_studies.json", "r") as f:
                all_studies = json.load(f)
            matches = match_studies(participant_data, all_studies)

            # Format & return the study summaries
            match_summary = format_matches_for_gpt(matches)
            return {"reply": match_summary}

        except Exception as e:
            return {"reply": "We encountered an error processing your info.", "error": str(e)}

    # 3) Otherwise, echo GPT’s prompt flow
    return {"reply": gpt_message}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
