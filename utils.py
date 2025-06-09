
def format_matches_for_gpt(matches):
    if not matches:
        return (
            "Unfortunately, no studies matched based on your details. "
            "Would you like us to follow up if new ones become available?"
        )

    summary = "Here are some clinical studies that may be a fit:\n"
    for i, study in enumerate(matches, 1):
        summary += f"\n🧪 **Study {i}** – *{study['title']}*\n"
        summary += f"- Location: {study.get('location', 'Not specified')}\n"
        summary += f"- Criteria: {study.get('criteria', 'Not provided')}\n"
        summary += f"- [View Study]({study['url']})\n"

    summary += "\nWould you like help signing up for any of these?"
    return summary
