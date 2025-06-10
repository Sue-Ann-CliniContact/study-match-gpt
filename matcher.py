import re
from geopy.distance import geodesic

def is_autism_related(text):
    autism_keywords = ["autism", "autistic", "ASD", "spectrum disorder"]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in autism_keywords)

def compute_score_and_distance(study, participant_coords):
    score = 0
    condition = study.get("condition_summary", "").lower()
    eligibility = study.get("eligibility", "").lower()
    keywords = ["autism", "asd", "autistic", "spectrum disorder"]
    if any(k in f"{condition} {eligibility}" for k in keywords):
        score += 5

    study_city = study.get("location", "")
    study_country = study.get("country", "")
    if study_country != "United States":
        return -1, None, None  # filter out non-US

    # City to coordinates (fallback to US center)
    city_coords = {
        "dallas": (32.7767, -96.7970),
        "boston": (42.3601, -71.0589),
        "bethesda": (38.9847, -77.0947),
        "new york": (40.7128, -74.0060),
        "san francisco": (37.7749, -122.4194),
        "nashville": (36.1627, -86.7816),
        "houston": (29.7604, -95.3698),
        "los angeles": (34.0522, -118.2437),
        "bronx": (40.8448, -73.8648),
        "stanford": (37.4275, -122.1697)
    }
    coords = city_coords.get(study_city.lower(), (38.0, -97.0))
    distance = geodesic(participant_coords, coords).miles

    if distance <= 25:
        score += 3
        distance_bucket = "Near You"
    elif distance <= 100:
        score += 2
        distance_bucket = "Regionally Close"
    else:
        score += 1
        distance_bucket = "National Reach"

    return score, distance, distance_bucket

def match_studies(participant, studies):
    matched = []
    try:
        age = int(participant.get("age", 0))
    except:
        age = 0

    participant_coords = (32.7767, -96.7970)
    pediatric_only = participant.get("study_age_focus", "").lower() == "pediatric"

    for study in studies:
        if not isinstance(study, dict):
            continue

        combined = (study.get("condition_summary", "") or "") + " " + (study.get("eligibility", "") or "")
        if not is_autism_related(combined):
            continue

        raw_min = study.get("min_age", "N/A")
        raw_max = study.get("max_age", "N/A")
        try:
            min_val = int(re.findall(r"\d+", raw_min)[0]) if re.findall(r"\d+", raw_min) else 0
            max_val = int(re.findall(r"\d+", raw_max)[0]) if re.findall(r"\d+", raw_max) else 120
        except:
            min_val, max_val = 0, 120

        if pediatric_only and max_val > 18:
            continue
        if not (min_val <= age <= max_val):
            continue

        score, distance, distance_bucket = compute_score_and_distance(study, participant_coords)
        if score < 0:
            continue

        # Normalize match confidence to 10
        match_confidence = round((score / 10) * 10, 1)
        if score >= 8:
            rationale = "Very strong match based on condition, location, and age"
        elif score >= 6:
            rationale = "Strong match based on condition and location"
        elif score >= 3:
            rationale = "Moderate match based on condition or proximity"
        else:
            rationale = "Possible match based on condition relevance"

        nct = study.get("nct_id", "")
        url = study.get("url") or (f"https://clinicaltrials.gov/ct2/show/{nct}" if nct else None)
        city = study.get("location", "N/A")
        summary = study.get("summary") or f"{study.get('title', '')} in {city}, recruiting ages {raw_min} to {raw_max}."

        match = {
            "nct_id":        nct,
            "title":         study.get("title", "No Title"),
            "description":   study.get("description", ""),
            "eligibility":   study.get("eligibility", ""),
            "min_age":       raw_min,
            "max_age":       raw_max,
            "location":      city,
            "state":         study.get("state", ""),
            "country":       study.get("country", ""),
            "status":        study.get("status", ""),
            "link":          study.get("link", url),
            "url":           url,
            "contact_name":  study.get("contact_name", "Not available"),
            "contact_email": study.get("contact_email", "Not available"),
            "contact_phone": study.get("contact_phone", "Not available"),
            "match_score":   score,
            "match_confidence": f"{match_confidence}/10",
            "summary":       summary,
            "match_reason":  rationale,
            "distance_bucket": distance_bucket,
        }
        matched.append(match)

    # Return top 10 by score
    return sorted(matched, key=lambda x: x["match_score"], reverse=True)[:10]
