import re
from geopy.distance import geodesic

def is_autism_related(text):
    autism_keywords = ["autism", "autistic", "ASD", "spectrum disorder"]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in autism_keywords)

def compute_score(study, participant_coords):
    score = 0
    condition = study.get("condition_summary", "").lower()
    eligibility = study.get("eligibility", "").lower()
    keywords = ["autism", "asd", "autistic", "spectrum disorder"]
    if any(k in f"{condition} {eligibility}" for k in keywords):
        score += 5

    study_city = study.get("location", "")
    study_country = study.get("country", "")
    if study_country != "United States":
        return -1  # filter out non-US

    # Map a few known cities, else fallback midpoint of U.S.
    if "dallas" in study_city.lower():
        coords = (32.7767, -96.7970)
    elif "boston" in study_city.lower():
        coords = (42.3601, -71.0589)
    elif "bethesda" in study_city.lower():
        coords = (38.9847, -77.0947)
    elif "new york" in study_city.lower():
        coords = (40.7128, -74.0060)
    else:
        coords = (38.0, -97.0)

    distance = geodesic(participant_coords, coords).miles
    if distance <= 25:
        score += 3
    elif distance <= 100:
        score += 2
    elif distance <= 300:
        score += 1

    return score

def match_studies(participant, studies):
    matched = []
    participant_coords = (32.7767, -96.7970)

    # Pediatric filter flag
    pediatric_only = participant.get("study_age_focus", "").lower() == "pediatric"
    try:
        age = int(participant.get("age", 0))
    except:
        age = 0

    for study in studies:
        if not isinstance(study, dict):
            continue

        # 1) Autism relevance
        combined = (study.get("condition_summary","") or "") + " " + (study.get("eligibility","") or "")
        if not is_autism_related(combined):
            continue

        # 2) Parse min/max age
        raw_min = study.get("min_age","N/A")
        raw_max = study.get("max_age","N/A")
        try:
            min_val = int(re.findall(r"\d+", raw_min)[0]) if re.findall(r"\d+", raw_min) else 0
            max_val = int(re.findall(r"\d+", raw_max)[0]) if re.findall(r"\d+", raw_max) else 120
        except:
            min_val, max_val = 0, 120

        # 3) Pediatric filter: drop any study with max_val > 18
        if pediatric_only and max_val > 18:
            continue

        # 4) Age eligibility
        if not (min_val <= age <= max_val):
            continue

        # 5) Compute score & rationale
        score = compute_score(study, participant_coords)
        if score < 0:
            continue
        rationale = []
        if score >= 8:
            rationale.append("Very strong match based on condition, location, and age")
        elif score >= 6:
            rationale.append("Strong match based on condition and location")
        elif score >= 3:
            rationale.append("Moderate match based on condition or proximity")
        else:
            rationale.append("Possible match based on condition relevance")

        # 6) Build match object
        nct = study.get("nct_id","")
        url = study.get("url") or (f"https://clinicaltrials.gov/ct2/show/{nct}" if nct else None)
        city = study.get("location","N/A")
        summary = study.get("summary") or f"{study.get('title','')} in {city}, recruiting ages {raw_min} to {raw_max}."

        match = {
            "nct_id":        nct,
            "title":         study.get("title","No Title"),
            "description":   study.get("description",""),
            "eligibility":   study.get("eligibility",""),
            "min_age":       raw_min,
            "max_age":       raw_max,
            "location":      city,
            "state":         study.get("state",""),
            "country":       study.get("country",""),
            "status":        study.get("status",""),
            "link":          study.get("link",url),
            "url":           url,
            "contact_name":  study.get("contact_name","Not available"),
            "contact_email": study.get("contact_email","Not available"),
            "contact_phone": study.get("contact_phone","Not available"),
            "match_score":   score,
            "summary":       summary,
            "match_reason":  rationale,
        }
        matched.append(match)

    # 7) Return only top 10 by match_score
    return sorted(matched, key=lambda x: x["match_score"], reverse=True)[:10]
