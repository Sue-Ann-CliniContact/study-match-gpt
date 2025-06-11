
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
            summary = m.get("summary", "").strip().replace("\n", " ").split(". ")
            short_summary = ". ".join(summary[:2]) + ("." if not summary[0].endswith('.') else "")
            eligibility_raw = m.get("eligibility", "").splitlines()
            eligibility = "\n".join(f"- {line.strip('- ')}" for line in eligibility_raw if line.strip())
            contact_info = " | ".join(filter(None, [m.get("contact_name"), m.get("contact_email"), m.get("contact_phone")]))

            out += (
                f"**{i}. {m['title']}**\n"
                f"**Location:** {m['location']}\n"
                f"**Link:** [View Study]({m['url']})\n"
                f"**Summary:** {short_summary}\n"
                f"**Eligibility:**\n{eligibility}\n"
                f"**Contact:** {contact_info}\n"
                f"**Match Confidence:** {m['match_score']}/10\n"
                f"**Match Rationale:** {rationale}\n\n"
            )
    return out.strip()
