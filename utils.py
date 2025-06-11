def calculate_proximity_score(participant_location, study_location):
    # Placeholder proximity score logic
    if participant_location and study_location:
        if participant_location.lower() in study_location.lower():
            return 10  # Exact city match
        elif participant_location.split(',')[-1].strip().lower() in study_location.lower():
            return 7  # State match
    return 4  # Distant

def is_eligible(participant, study):
    age = participant.get("age")
    min_age = study.get("min_age_years")
    max_age = study.get("max_age_years")

    # ✅ Prevent TypeError from None values
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
