import re
from geopy.distance import geodesic

def is_autism_related(text: str) -> bool:
    keywords = ["autism", "autistic", "asd", "spectrum disorder"]
    tl = text.lower()
    return any(k in tl for k in keywords)

def compute_score_and_group(study: dict, user_loc: tuple) -> tuple:
    score = 0
    group = "Other"

    combined = f"{study.get('condition_summary','')} {study.get('eligibility','')}"
    if is_autism_related(combined):
        score += 5
# Boost score if participant's comorbid conditions match those listed in eligibility
    participant_conditions = participant_data.get("co_conditions", "").lower()
    eligibility_text = study.get("eligibility", "").lower()
    if any(cond in eligibility_text for cond in participant_conditions.split(",") if cond.strip()):
        score += 1
# Boost score if study mentions remote/online participation
    if "remote" in eligibility_text or "online" in eligibility_text:
        score += 1

    coords = study.get("coordinates")
    if user_loc and coords:
        lat2, lon2 = coords if isinstance(coords, (list, tuple)) else (coords["lat"], coords["lon"])
        dist = geodesic(user_loc, (lat2, lon2)).miles
        if dist <= 50:
            score += 3
            group = "Near You"
        elif dist <= 300:
            score += 2
            group = "National"
    else:
        score += 1

    return score, group

def parse_age_to_years(value) -> int:
    if not value:
        return None
    text = str(value).lower().strip()
    match = re.search(r"(\d+)\s*(year|month)", text)
    if match:
        number = int(match.group(1))
        unit = match.group(2)
        return number if unit == "year" else round(number / 12)
    digits = re.findall(r"\d+", text)
    return int(digits[0]) if digits else None

def match_studies(participant: dict, studies: list) -> list:
    user_loc = participant.get("location")
    user_age = participant.get("age")
    if user_age is None:
        return []

    results = []

    for s in studies:
        min_a = parse_age_to_years(s.get("min_age")) or 0
        max_a = parse_age_to_years(s.get("max_age")) or 120

        if not (min_a <= user_age <= max_a):
            continue

        score, group = compute_score_and_group(s, user_loc)
        if score <= 0:
            continue

        rationale = []
        if is_autism_related(f"{s.get('condition_summary','')} {s.get('eligibility','')}"):
            rationale.append("Autism relevance")
        rationale.append(f"Age range {min_a}-{max_a}")
        rationale.append(f"Proximity score {score}")

        contact_parts = []
        if s.get("contact_name"):
            contact_parts.append(s["contact_name"])
        if s.get("contact_email"):
            contact_parts.append(s["contact_email"])
        if s.get("contact_phone"):
            contact_parts.append(s["contact_phone"])
        contact = " | ".join(contact_parts).strip()

        results.append({
            "study_title": s.get("title") or s.get("brief_title") or "No Title",
            "location": f"{s.get('location')}, {s.get('state')}",
            "study_link": s.get("url") or f"https://clinicaltrials.gov/ct2/show/{s.get('nct_id','')}",
            "summary": s.get("brief_summary") or s.get("description", "No summary"),
            "eligibility": s.get("eligibility") or "Not provided",
            "contact": contact or "Not available",
            "match_confidence": score,
            "match_rationale": "; ".join(rationale),
            "group": group
        })

    results.sort(key=lambda x: x["match_confidence"], reverse=True)
    return results[:10]
