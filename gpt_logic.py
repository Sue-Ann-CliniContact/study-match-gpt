import os
import openai
import re
from typing import List, Dict, Any

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store user data progressively
user_data = {}

def extract_user_info(message: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts age and location from a message."""
    age_match = re.search(r'(\d+)\s*(year|yr)[s]?\s*old', message.lower())
    city_state_match = re.search(r'in\s+([A-Za-z\s]+,\s*[A-Za-z]{2})', message)

    if age_match:
        user_data['age'] = int(age_match.group(1))
    if city_state_match:
        user_data['location'] = city_state_match.group(1).strip()

    return user_data

def check_info_complete(user_data: Dict[str, Any]) -> bool:
    return 'age' in user_data and 'location' in user_data

def run_chat(message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    global user_data
    user_data = extract_user_info(message, user_data)

    # Prepare chat history with user data for future use (e.g., backend logic or saving to DB)
    chat_with_context = history.copy()
    chat_with_context.append({"role": "user", "content": message})

    if 'age' in user_data:
        chat_with_context.append({"role": "system", "content": f"Age provided: {user_data['age']} years old."})
    if 'location' in user_data:
        chat_with_context.append({"role": "system", "content": f"Location provided: {user_data['location']}."})

    # Determine next step or generate GPT response
    if not check_info_complete(user_data):
        if 'age' not in user_data:
            return {
                "reply": "How old are you or the person you're searching for?",
                "user_data": user_data
            }
        if 'location' not in user_data:
            return {
                "reply": "Please tell me the city and state (or just the state) where you're located.",
                "user_data": user_data
            }
    else:
        reply = f"Thanks! Searching for studies for a {user_data['age']}-year-old in {user_data['location']}... 🔍"
        return {
            "reply": reply,
            "user_data": user_data
        }

    return {
        "reply": "Thanks! Please continue.",
        "user_data": user_data
    }
