import math
from datetime import datetime

def format_matches_for_gpt(matches: list) -> str:
    if not matches:
        return "Unfortunately, no studies matched based on your details."

    out = "Here are some clinical studies that may be a fit:\n\n"
    for i, m in enumerate(matches, 1):
        rationale = ", ".join(r for r in m.get("match_reason", []) if r)
        out += (
            f"**{i}. {m['title']}**\n"
            f"- Location: {m['location']}\n"
            f"- Study Link: [View Study]({m['url']})\n"
            f"- Summary: {m['summary']}\n"
            f"- Eligibility: {m['eligibility']}\n"
            f"- Contact: {m['contact_name']} | {m['contact_email']} | {m['contact_phone']}\n"
            f"- Match Confidence: {m['match_score']}/10\n"
            f"- Match Rationale: {rationale}\n\n"
        )
    return out.strip()
