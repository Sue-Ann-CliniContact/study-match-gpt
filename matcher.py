import re
from geopy.distance import geodesic

def is_autism_related(text):
    autism_keywords = ["autism", "autistic", "ASD", "spectrum disorder"]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in autism_keywords)

def compute_score(study, participant_coords):
    score = 0
    # Boost for condition/eligibility keywords
    condition = study.get("condition_summary", "").lower()
    eligibility = study.get("eligibility", "").lower()
    keywords = ["autism", "asd", "autistic", "spectrum disorder"]
    if any(k in f"{condition} {eligibility}" for k in keywords):
        score += 5

    # Location-based scoring
    study_city = study.get("location", "")
    study_country = study.get("country", "")
    if study_country != "United States":
        return -1  # exclude non-US studies
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
    matched_studies = []
    # Default participant coords (Dallas)
    participant_coords = (32.7767, -96.7970)
    try:
        age = int(participant.get("age", 0))
    except:
        age = 0

    for study in studies:
        try:
            if not isinstance(study, dict):
                continue

            # 1. Autism relevance check
            text = (study.get("condition_summary", "") or "") + " " + (study.get("eligibility", "") or "")
            if not is_autism_related(text):
                continue

            # 2. Age eligibility
            min_raw = study.get("min_age", "N/A")
            max_raw = study.get("max_age", "N/A")
            try:
                min_val = int(re.findall(r"\d+", min_raw)[0]) if re.findall(r"\d+", min_raw) else 0
                max_val = int(re.findall(r"\d+", max_raw)[0]) if re.findall(r"\d+", max_raw) else 120
            except:
                min_val, max_val = 0, 120
            if not (min_val <= age <= max_val):
                continue

            # 3. Compute score and build rationale
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

            # 4. Build match dictionary with full fields
            nct = study.get("nct_id", "")
            url = study.get("url") or (f"https://clinicaltrials.gov/ct2/show/{nct}" if nct else None)
            city = study.get("location", "N/A")
            title = study.get("title", "No Title")
            summary = study.get("summary") or f"{title} in {city}, recruiting ages {min_raw} to {max_raw}."

            match = {
                "nct_id": nct,
                "title": title,
                "description": study.get("description", ""),
                "eligibility": study.get("eligibility", ""),
                "min_age": min_raw,
                "max_age": max_raw,
                "location": city,
                "state": study.get("state", ""),
                "country": study.get("country", ""),
                "status": study.get("status", ""),
                "link": study.get("link", url),
                "url": url,
                "contact_name": study.get("contact_name", "Not available"),
                "contact_email": study.get("contact_email", "Not available"),
                "contact_phone": study.get("contact_phone", "Not available"),
                "match_score": score,
                "summary": summary,
                "match_reason": rationale,
            }
            matched_studies.append(match)
        except:
            continue

    # Return top 10 matches by score
    return sorted(matched_studies, key=lambda x: x["match_score"], reverse=True)[:10]