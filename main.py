import os
import json
import re
import openai
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from matcher import match_studies
from utils import extract_participant_data, format_matches_for_gpt, calculate_age
from push_to_monday import push_to_monday
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
#                         YOUR ORIGINAL SYSTEM PROMPT
# ──────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are Hey Trial, a friendly assistant for CliniContact.
Your job is to help parents and individuals find suitable autism research studies.
Use the conversation to:
1. Collect participant information (name, DOB, location, diagnosis, verbal status, etc.).
2. Push that data to Monday.com via the push_to_monday() function.
3. Then match against your indexed_studies.json using match_studies().
4. Finally, format the matches with grouping ("Near You", "National", "Other"),
   include match scores, rationales, and full study details (link, summary, eligibility, contact).
Always maintain a conversational tone, guiding the user step by step.
"""
# ──────────────────────────────────────────────────────────────────────────────

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_histories = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    session = req.session_id or "default"
    user_msg = req.message

    # Initialize history if new session
    if session not in chat_histories:
        chat_histories[session] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Append user message
    chat_histories[session].append({"role": "user", "content": user_msg})

    # Ask GPT for next step (data extraction or final reply)
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_histories[session],
        temperature=0.5,
    )
    assistant_msg = completion.choices[0].message["content"]
    chat_histories[session].append({"role": "assistant", "content": assistant_msg})

    # If GPT returned JSON payload, parse & match
    json_match = re.search(r'\\{[\\s\\S]*\\}', assistant_msg)
    if json_match:
        try:
            raw_data = json.loads(json_match.group())
            # Compute age from DOB and add to data
            raw_data["age"] = calculate_age(raw_data.get("dob", ""))
            # Normalize participant data
            participant = extract_participant_data(raw_data)
            # Push to Monday.com
            push_to_monday(participant)
            # Load studies index
            with open("indexed_studies.json", "r", encoding="utf-8") as f:
                studies = json.load(f)
            # Find matches
            raw_matches = match_studies(participant, studies)
            # Format for GPT reply
            reply = format_matches_for_gpt(raw_matches)
            return {"reply": reply}
        except Exception as e:
            # Fallback error message
            return {"reply": "We encountered an error processing your info.", "error": str(e)}

    # Otherwise, just return GPT's conversational answer
    return {"reply": assistant_msg}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
