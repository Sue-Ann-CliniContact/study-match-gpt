from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from matcher import match_studies
from utils import extract_participant_data
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_input: str
    chat_history: list

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        participant_data = extract_participant_data(request.chat_history)
        matches = match_studies(participant_data)
        return {"reply": matches}
    except Exception as e:
        return {"reply": "We encountered an error processing your info.", "error": str(e)}