def format_matches_for_gpt(matches):
    if not matches:
        return (
            "Unfortunately, no studies matched based on your details. "
            "Would you like us to follow up if new ones become available?"
        )

    output = "Here are some clinical studies that may be a fit:\n\n"
    for idx, study in enumerate(matches, 1):
        # Build rationale text
        reasons = study.get("match_reason", [])
        rationale_text = "; ".join(reasons) if reasons else "No specific rationale provided."

        output += f"**{idx}. {study['title']}**\n"
        output += f"- **Location**: {study['location']}, {study['state']}\n"
        output += f"- **Study Link**: [View Study]({study['url']})\n"
        output += f"- **Summary**: {study['summary']}\n"
        output += f"- **Eligibility Overview**: {study['eligibility'] or 'Not provided'}\n"
        output += (
            f"- **Contact**: {study['contact_name']} | "
            f"{study['contact_email']} | {study['contact_phone']}\n"
        )
        output += f"- **Match Rationale**: {rationale_text}\n\n"

    return output.strip()
