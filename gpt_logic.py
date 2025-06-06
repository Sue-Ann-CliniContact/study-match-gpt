import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def run_chat(user_input, conversation_history=[]):
    system_message = {
        "role": "system",
        "content": (
            "You are Hey Trial — a friendly, trustworthy, and helpful digital guide that supports people interested "
            "in participating in clinical research. You specialize in helping users find autism-related studies. "
            "You speak clearly, ask one question at a time, and make users feel understood and supported. "
            "Only show studies after confirming basic details (like age, location, and diagnosis). "
            "Use a warm and welcoming tone, and always explain what you’re doing next."
        )
    }

    messages = [system_message] + conversation_history + [{"role": "user", "content": user_input}]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )

    assistant_reply = response["choices"][0]["message"]["content"]
    return assistant_reply