import os
import json
import re
import openai
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from matcher import match_studies
from utils import format_matches_for_gpt
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

def calculate_age(dob_str: str) -> int:
    for fmt in ("%B %d, %Y", "%d %B %Y", "%d %b %Y", "%Y-%m-%d"):
        try:
            dob = datetime.strptime(dob_str, fmt)
            today = datetime.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except:
            continue
    return 0

@app.post("/chat")
async def chat_handler(req: ChatRequest):
    session = req.session_id or "default"
    user_msg = req.message

    if session not in chat_histories:
        chat_histories[session] = [{"role": "system", "content": SYSTEM_PROMPT}]

    chat_histories[session].append({"role": "user", "content": user_msg})

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_histories[session],
        temperature=0.5,
    )
    assistant_msg = completion.choices[0].message["content"]
    chat_histories[session].append({"role": "assistant", "content": assistant_msg})

    # If GPT returned JSON, parse & match
    if "{" in assistant_msg and "}" in assistant_msg:
        try:
            start = assistant_msg.index("{")
            end = assistant_msg.rindex("}") + 1
            json_str = assistant_msg[start:end]
            data = json.loads(json_str)

            data["age"] = calculate_age(data.get("dob", ""))
            participant = data  # keep raw keys for matcher
            push_to_monday(participant)
        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            print("⚠️ Failed to parse JSON from GPT response.")
            print("Raw assistant message:\n", assistant_msg)
            print("Error:\n", str(e))

            with open("indexed_studies.json", "r", encoding="utf-8") as f:
                studies = json.load(f)
            raw_matches = match_studies(participant, studies)
            reply = format_matches_for_gpt(raw_matches)
            return {"reply": reply}
        except Exception as e:
            return {"reply": "We encountered an error processing your info.", "error": str(e)}

    return {"reply": assistant_msg}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
