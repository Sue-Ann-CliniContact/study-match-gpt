def format_matches_for_gpt(matches):
    if not matches:
        return (
            "Unfortunately, no studies matched based on your details. "
            "Would you like us to follow up if new ones become available?"
        )

    # Group by distance bucket
    grouped = {"Near you": [], "National": [], "Remote": []}
    for study in matches:
        bucket = study.get("distance_bucket", "National")
        grouped.setdefault(bucket, []).append(study)

    output = "Here are some clinical studies that may be a fit:\n\n"

    for group_label in ["Near you", "National", "Remote"]:
        group = grouped.get(group_label, [])
        if not group:
            continue

        output += f"### {group_label}\n\n"
        for idx, study in enumerate(group, 1):
            reasons = study.get("match_reason", [])
            rationale = "; ".join(reasons) if reasons else 'No specific rationale provided.'

            score = study.get("match_score")
            if score:
                score_str = f"{score:.1f}/10"
            else:
                score_str = "N/A"

            output += f"**{idx}. {study['title']}** (Match Score: {score_str})\n"
            output += f"- **Location**: {study['location']}, {study['state']}\n"
            output += f"- **Study Link**: [View Study]({study['url']})\n"
            output += f"- **Summary**: {study['summary']}\n"
            output += f"- **Eligibility Overview**: {study['eligibility'] or 'Not provided'}\n"
            output += (
                f"- **Contact**: {study['contact_name']} | {study['contact_email']} | {study['contact_phone']}\n"
            )
            output += f"- **Match Rationale**: {rationale}\n\n"

    return output.strip()
