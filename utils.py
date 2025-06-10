def format_matches_for_gpt(matches):
    if not matches:
        return "Unfortunately, no studies matched based on your details. Would you like us to follow up if new ones become available?"

    output = "Here are some studies that may be a good fit:\n\n"
    for idx, study in enumerate(matches, 1):
        rationale = []
        if study["match_score"] >= 8:
            rationale.append("Very strong match based on condition, location, and age")
        elif study["match_score"] >= 6:
            rationale.append("Strong match based on condition and location")
        elif study["match_score"] >= 3:
            rationale.append("Moderate match based on condition or proximity")

        output += f"""**{idx}. {study['title']}**
📍 Location: {study['location']}, {study['state']}
🔗 [View Study]({study['url']})
📋 Summary: {study['summary']}
🧬 Eligibility: {study['eligibility'] or 'Not specified'}
📞 Contact: {study['contact_name']} | {study['contact_email']} | {study['contact_phone']}
✅ Match Reason: {"; ".join(rationale)}

"""
    return output
