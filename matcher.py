import re
from geopy.distance import geodesic

def extract_age_from_text(text):
    if not text:
        return None, None
    matches = re.findall(r'(\d+)\s*(?:to|-|–|and)?\s*(\d+)?\s*(year|month|week)?', text.lower())
    if matches:
        try:
            min_val = int(matches[0][0])
            max_val = int(matches[0][1]) if matches[0][1] else 120
            unit = matches[0][2] if matches[0][2] else "year"
            if unit.startswith("week"):
                min_val = round(min_val / 52, 2)
                max_val = round(max_val / 52, 2)
            elif unit.startswith("month"):
                min_val = round(min_val / 12, 2)
                max_val = round(max_val / 12, 2)
            return min_val, max_val
        except:
            return None, None
    return None, None

def is_autism_related(text):
    if not text:
        return False
    keywords = ["autism", "asd", "autistic", "spectrum disorder"]
    text = text.lower()
    return any(kw in text for kw in keywords)

def match_studies(participant, studies):
    user_age = participant.get("age")
    user_loc = participant.get("location")
    user_city = participant.get("location_city", "").lower()
    user_state = participant.get("location_state", "").lower()

    if user_age is None:
        return []

    results = []

    for s in studies:
        if s.get("recruitment_status", "").lower() != "recruiting":
            continue

        min_age = s.get("min_age_years")
        max_age = s.get("max_age_years")
        if min_age is None or max_age is None:
            min_age, max_age = extract_age_from_text(s.get("eligibility_text", ""))
            min_age = min_age if min_age is not None else 0
            max_age = max_age if max_age is not None else 120

        if not (min_age <= user_age <= max_age):
            continue

        score = 0
        rationale = []

        if is_autism_related(" ".join([s.get("study_title", ""), s.get("eligibility_text", "")])):
            score += 3
            rationale.append("Autism relevance")

        loc_str = s.get("location", "").lower()
        if user_city and user_city in loc_str:
            score += 4
            rationale.append("Same city")
        elif user_state and user_state in loc_str:
            score += 2
            rationale.append("Same state")
        else:
            score += 1
            rationale.append("National match")

        score += 2  # for age match
        rationale.append(f"Age range {min_age}-{max_age}")

        contact_parts = []
        if s.get("contact_name"):
            contact_parts.append(s["contact_name"])
        if s.get("contact_email"):
            contact_parts.append(s["contact_email"])
        if s.get("contact_phone"):
            contact_parts.append(s["contact_phone"])
        contact = " | ".join(filter(None, contact_parts)) or "Not available"

        results.append({
            "study_title": s.get("study_title") or "No Title",
            "location": s.get("location") or "Unknown",
            "study_link": s.get("study_link"),
            "summary": s.get("summary") or "",
            "eligibility": s.get("eligibility_text") or "Not provided",
            "contact": contact,
            "match_confidence": score,
            "match_rationale": "; ".join(rationale),
            "group": "Matched"
        })

    results.sort(key=lambda x: x["match_confidence"], reverse=True)
    return results[:10]