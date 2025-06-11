import re
from geopy.distance import geodesic

def extract_age_from_text(text):
    matches = re.findall(r'(\d+)\s*(?:to|-|–|and)?\s*(\d+)?\s*(?:years|yrs)?', text.lower())
    if matches:
        try:
            min_age = int(matches[0][0])
            max_age = int(matches[0][1]) if matches[0][1] else 120
            return min_age, max_age
        except:
            return None, None
    return None, None

def is_autism_related(text: str) -> bool:
    keywords = ["autism", "asd", "autistic", "spectrum disorder"]
    tl = text.lower()
    hits = sum(1 for k in keywords if k in tl)
    return hits >= 2  # Require at least 2 keyword matches for stronger match

def compute_score_and_group(study, user_loc, user_age):
    score = 0
    group = "Other"
    full_text = " ".join([
        study.get("study_title", ""),
        study.get("summary", ""),
        study.get("eligibility_text", "")
    ])

    if is_autism_related(full_text):
        score += 5
    else:
        score -= 1

    coords = study.get("coordinates")
    if user_loc and coords:
        lat2, lon2 = coords if isinstance(coords, (list, tuple)) else (coords["lat"], coords["lon"])
        dist = geodesic(user_loc, (lat2, lon2)).miles
        if dist <= 30:
            score += 5
            group = "Near You"
        elif dist <= 100:
            score += 4
            group = "Driving Distance"
        elif dist <= 300:
            score += 3
            group = "Regional"
        elif dist <= 1000:
            score += 2
            group = "National"
        else:
            score += 1
            group = "Far/National"
    else:
        score += 1

    min_age = study.get("min_age_years", 0)
    max_age = study.get("max_age_years", 120)
    if user_age is not None and user_age <= 17:
        if max_age <= 18:
            score += 2
        elif min_age <= 5 and max_age <= 25:
            score += 1

    return score, group

def match_studies(participant, studies):
    user_age = participant.get("age")
    user_loc = participant.get("location")
    if user_age is None:
        return []

    results = []

    for s in studies:
        if s.get("recruitment_status", "").lower() != "recruiting":
            continue

        min_a = s.get("min_age_years")
        max_a = s.get("max_age_years")

        if min_a is None or max_a is None:
            min_a_fallback, max_a_fallback = extract_age_from_text(s.get("eligibility_text", ""))

            if min_a is None and min_a_fallback is not None:
                min_a = min_a_fallback

            if max_a is None and max_a_fallback is not None:
                max_a = max_a_fallback

        if min_a is None or max_a is None:
            continue

        if not (min_a <= user_age <= max_a):
            continue

        score, group = compute_score_and_group(s, user_loc, user_age)
        if score <= 0:
            continue

        rationale = []
        if is_autism_related(" ".join([s.get("study_title", ""), s.get("eligibility_text", "")])):
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
        contact = " | ".join(contact_parts) if contact_parts else "Not available"

        results.append({
            "study_title": s.get("study_title") or "No Title",
            "location": s.get("location") or "Unknown",
            "study_link": s.get("study_link") or f"https://clinicaltrials.gov/ct2/show/{s.get('nct_id','')}",
            "summary": s.get("summary") or "No summary.",
            "eligibility": s.get("eligibility_text") or "Not provided",
            "contact": contact,
            "match_confidence": score,
            "match_rationale": "; ".join(rationale),
            "group": group
        })

    results.sort(key=lambda x: x["match_confidence"], reverse=True)
    return results[:10]
