def calculate_proximity_score(participant_location, study_location):
    if participant_location and study_location:
        if participant_location.lower() in study_location.lower():
            return 10
        elif participant_location.split(',')[-1].strip().lower() in study_location.lower():
            return 7
    return 4

def is_eligible(participant, study):
    age = participant.get("age")
    min_age = study.get("min_age_years")
    max_age = study.get("max_age_years")

    if age is not None:
        if min_age is not None and age < min_age:
            return False
        if max_age is not None and age > max_age:
            return False

    return True

def format_phone_number(number):
    if not number:
        return ""
    cleaned = ''.join(filter(str.isdigit, number))
    if cleaned.startswith("1") and len(cleaned) == 11:
        return f"+{cleaned}"
    elif len(cleaned) == 10:
        return f"+1{cleaned}"
    return f"+{cleaned}" if cleaned else ""

def format_email(email):
    return email.strip() if email else ""

def normalize_string(text):
    return text.lower().strip() if isinstance(text, str) else ""

def format_matches_for_gpt(matches):
    if not matches:
        return "Sorry, we couldn’t find any matching studies based on the information provided."

    lines = ["Here are some clinical studies that may be a fit:\n"]

    for match in matches:
        lines.append(f"**{match.get('study_title', 'Untitled Study')}**")
        lines.append(f"**Location:** {match.get('location', 'N/A')}")
        lines.append(f"**Study Link:** [{match.get('study_link', 'View Study')}]({match.get('study_link', '')})")

        # 2-line summary
        summary = match.get("summary", "")
        if summary:
            sentences = summary.strip().split(". ")
            brief_summary = ". ".join(sentences[:2]).strip()
            if not brief_summary.endswith("."):
                brief_summary += "."
            lines.append(f"**Summary:** {brief_summary}")

        # Bullet-point eligibility
        eligibility_text = match.get("eligibility", "").strip()
        if eligibility_text:
            bullets = []
            for line in eligibility_text.splitlines():
                stripped = line.strip("•*-– ")
                if len(stripped) > 3:
                    bullets.append(f"- {stripped}")
            if bullets:
                lines.append("**Eligibility:**")
                lines.extend(bullets[:5])  # Limit to 5 bullets to reduce verbosity

        # Contact
        contact = match.get("contact", "")
        if contact and contact.lower() != "none":
            lines.append(f"**Contact:** {contact}")

        # Match Details
        confidence = match.get("match_confidence")
        rationale = match.get("match_rationale", "")
        lines.append(f"**Match Confidence:** {confidence}/10" if confidence else "")
        lines.append(f"**Match Rationale:** {rationale}")

        lines.append("\n")  # spacer

    return "\n".join(lines).strip()
