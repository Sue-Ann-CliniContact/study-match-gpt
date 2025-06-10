
def format_matches_for_gpt(matches: list) -> str:
    if not matches:
        return "Unfortunately, no studies matched based on your details."

    grouped = {"Near You": [], "National": [], "Other": []}
    for m in matches:
        group = m.get("group", "Other")
        grouped.setdefault(group, []).append(m)

    out = "Here are some clinical studies that may be a fit:\n\n"

    for group_label in ["Near You", "National", "Other"]:
        group_matches = grouped.get(group_label, [])
        if not group_matches:
            continue
        out += f"### {group_label} Studies\n\n"
        for i, m in enumerate(group_matches, 1):
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
