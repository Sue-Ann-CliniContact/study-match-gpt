from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import matcher
from utils import parse_user_input

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    chat_history: list
    user_input: str

@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    chat_history = chat_request.chat_history
    user_input = chat_request.user_input

    # Parse participant data from chat
    participant_data = parse_user_input(chat_history, user_input)

    # Get study matches
    matched_studies = matcher.match_studies(participant_data)

    # Group and format response
    grouped_response = group_and_format_studies(matched_studies)

    return {"reply": grouped_response}


def group_and_format_studies(matched_studies):
    from collections import defaultdict

    grouped = defaultdict(list)
    for match in matched_studies:
        bucket = match.get("distance_bucket", "Other")
        grouped[bucket].append(match)

    output = "Here are some clinical studies that may be a fit:\n\n"
    order = ["Near You", "In Your State", "National", "Other"]

    for bucket in order:
        if bucket in grouped:
            output += f"## {bucket} Studies\n\n"
            sorted_studies = sorted(grouped[bucket], key=lambda x: x["score"], reverse=True)
            for i, item in enumerate(sorted_studies, 1):
                study = item["study"]
                output += (
                    f"{i}. **{study.get('brief_title', 'Untitled Study')}**\n"
                    f"- **Location**: {study.get('location', 'N/A')}\n"
                    f"- **Study Link**: [View Study]({study.get('url', '#')})\n"
                    f"- **Summary**: {study.get('brief_summary', 'No summary provided.')}\n"
                    f"- **Eligibility Overview**: {study.get('eligibility', 'No eligibility details.')}\n"
                    f"- **Contact**: {study.get('contact_name', 'N/A')} | {study.get('contact_email', 'N/A')} | {study.get('contact_phone', 'N/A')}\n"
                    f"- **Match Confidence**: {item.get('score', 0):.1f}/10\n"
                    f"- **Match Rationale**: {item.get('match_rationale', 'N/A')}\n\n"
                )

    return output.strip()
