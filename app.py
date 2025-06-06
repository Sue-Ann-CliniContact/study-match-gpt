from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gpt_logic import run_chat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []  # list of {"role": "user"/"assistant", "content": "..."}

@app.post("/chat")
async def chat(request: ChatRequest):
    reply = run_chat(request.message, request.history)
    return {"reply": reply}
