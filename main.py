
from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
import os
import json
import re
from matcher import match_studies
from utils import format_matches_for_gpt

openai.api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()

SYSTEM_PROMPT = """You are a clinical trial assistant named Hey Trial. Your job is to collect the following info one-by-one in a conversational tone:
- Name of participant (optional)
- Age (required)
- Location (required)
- Diagnosis (must mention autism)
- Other medical conditions
- Phone number
- Email address

Ask only one question at a time in a friendly tone. Use the user's previous answers to skip ahead. Never repeat questions.

Once all info is collected, return this dictionary only:

{
  "name": ...,
  "age": ...,
  "location": ...,
  "diagnosis": ...,
  "phone": ...,
  "email": ...,
  "other_conditions": ...
}

Say nothing else in that message. Do not try to match or explain yet."""

chat_histories = {}

@app.post("/chat")
async def chat_handler(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "default")
    user_input = body.get("message")

    if session_id not in chat_histories:
        chat_histories[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    chat_histories[session_id].append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_histories[session_id],
        temperature=0.5
    )

    gpt_message = response.choices[0].message["content"]
    chat_histories[session_id].append({"role": "assistant", "content": gpt_message})

    match = re.search(r'{[\s\S]*}', gpt_message)
    if match:
        try:
            participant_data = json.loads(match.group())
            with open("indexed_studies.json", "r") as f:
                all_studies = json.load(f)
            matches = match_studies(participant_data, all_studies)
            match_summary = format_matches_for_gpt(matches)
            chat_histories[session_id].append({"role": "user", "content": match_summary})
            followup_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=chat_histories[session_id],
                temperature=0.5
            )
            final_reply = followup_response.choices[0].message["content"]
            return {"reply": final_reply}
        except Exception as e:
            return {"reply": "We encountered an error processing your info.", "error": str(e)}

    return {"reply": gpt_message}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
