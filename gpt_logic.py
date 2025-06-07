import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_chat(user_input, history=[]):
    system = {
        "role": "system",
        "content": (
            "You are Hey Trial — a friendly, supportive assistant helping users find autism research studies "
            "that match their age, location, and diagnosis. Ask one question at a time, be warm, and explain clearly. "
            "If you receive structured results, return them cleanly and clearly grouped by study."
        )
    }
    messages = [system] + history + [{"role": "user", "content": user_input}]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content