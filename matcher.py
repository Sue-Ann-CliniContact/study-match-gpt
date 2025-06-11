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
        score += 1  # Reward for having some info even if coords missing

    return score, group

def safe_parse_age(value, fallback):
    try:
        return int(re.findall(r"\d+", str(value))[0])
    except:
        return fallback

def match_studies(participant: dict, studies: list) -> list:
    user_loc = participant.get("location")
    user_age = participant.get("age")
    if user_age is None:
        return []

    pediatric_only = participant.get("study_age_focus", "pediatric").lower().startswith("ped")

    results = []
    for s in studies:
        min_a = safe_parse_age(s.get("min_age"), 0)
        max_a = safe_parse_age(s.get("max_age"), 120)

        if pediatric_only and max_a > 18:
            continue
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

        results.append({
            "title": s.get("title") or s.get("brief_title") or "No Title",
            "location": f"{s.get('location')}, {s.get('state')}",
            "url": s.get("url") or f"https://clinicaltrials.gov/ct2/show/{s.get('nct_id','')}",
            "summary": s.get("brief_summary") or s.get("description", "No summary"),
            "eligibility": s.get("eligibility") or "Not provided",
            "contact_name": s.get("contact_name", "Not available"),
            "contact_email": s.get("contact_email", "Not available"),
            "contact_phone": s.get("contact_phone", "Not available"),
            "match_score": score,
            "match_reason": rationale,
            "group": group
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:10]
