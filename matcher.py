# matcher.py (updated)
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
    # filter out non-US
    if study_country != "United States":
        return -1

    # determine study coordinates
    if "dallas" in study_city.lower():
        study_coords = (32.7767, -96.7970)
    elif "boston" in study_city.lower():
        study_coords = (42.3601, -71.0589)
    elif "bethesda" in study_city.lower():
        study_coords = (38.9847, -77.0947)
    elif "new york" in study_city.lower():
        study_coords = (40.7128, -74.0060)
    else:
        study_coords = (38.0, -97.0)

    distance = geodesic(participant_coords, study_coords).miles
    if distance <= 25:
        score += 3
    elif distance <= 100:
        score += 2
    elif distance <= 300:
        score += 1

    return score

def match_studies(participant, studies):
    matched_studies = []
    participant_coords = (32.7767, -96.7970)  # Dallas fallback
    age = participant.get("age", 0)
    try:
        age = int(age)
    except:
        age = 0

    for study in studies:
        try:
            if not isinstance(study, dict):
                continue

            # autism relevance
            combined_text = (study.get("condition_summary", "") or "") + " " + (study.get("eligibility", "") or "")
            if not is_autism_related(combined_text):
                continue

            # parse age bounds
            min_age_raw = study.get("min_age", "N/A")
            max_age_raw = study.get("max_age", "N/A")
            try:
                min_age_val = int(re.findall(r"\d+", min_age_raw)[0]) if re.findall(r"\d+", min_age_raw) else 0
                max_age_val = int(re.findall(r"\d+", max_age_raw)[0]) if re.findall(r"\d+", max_age_raw) else 120
            except:
                min_age_val, max_age_val = 0, 120

            if not (min_age_val <= age <= max_age_val):
                continue

            # compute score and rationale
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

            # build match object
            nct_id = study.get("nct_id", "")
            url = study.get("url") or (f"https://clinicaltrials.gov/ct2/show/{nct_id}" if nct_id else None)
            link = study.get("link", url)
            city = study.get("location", "Location N/A")
            title = study.get("title", "No Title")
            summary = study.get("summary") or f"{title} in {city}, recruiting ages {min_age_raw} to {max_age_raw}."

            match = {
                "nct_id": nct_id,
                "title": title,
                "description": study.get("description", ""),
                "eligibility": study.get("eligibility", ""),
                "min_age": min_age_raw,
                "max_age": max_age_raw,
                "location": city,
                "state": study.get("state", ""),
                "country": study.get("country", ""),
                "status": study.get("status", ""),
                "link": link,
                "url": url,
                "contact_name": study.get("contact_name", "Not available"),
                "contact_email": study.get("contact_email", "Not available"),
                "contact_phone": study.get("contact_phone", "Not available"),
                "match_score": score,
                "summary": summary,
                "match_reason": rationale,
            }
            matched_studies.append(match)
        except Exception:
            continue

    return sorted(matched_studies, key=lambda x: x["match_score"], reverse=True)[:10]