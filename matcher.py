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
    study_state = study.get("state", "")
    study_country = study.get("country", "")
    study_coords = (0, 0)

    if study_country != "United States":
        print(f"Skipping international study: {study.get('title')}")
        return -1  # filter out non-US by default

    if "dallas" in study_city.lower():
        study_coords = (32.7767, -96.7970)
    elif "boston" in study_city.lower():
        study_coords = (42.3601, -71.0589)
    elif "bethesda" in study_city.lower():
        study_coords = (38.9847, -77.0947)
    elif "new york" in study_city.lower():
        study_coords = (40.7128, -74.0060)
    else:
        study_coords = (38.0, -97.0)  # default fallback

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
    participant_coords = (32.7767, -96.7970)  # hardcoded Dallas for now

    for study in studies:
        try:
            if not isinstance(study, dict):
                continue

            # Autism relevance check
            combined_text = (study.get("condition_summary", "") or "") + " " + (study.get("eligibility", "") or "")
            if not is_autism_related(combined_text):
                print(f"Skipping non-autism study: {study.get('title')}")
                continue

            # Parse age limits
            min_age = study.get("min_age", "0")
            max_age = study.get("max_age", "120")
            try:
                min_age_val = int(re.findall(r"\d+", min_age)[0]) if re.findall(r"\d+", min_age) else 0
                max_age_val = int(re.findall(r"\d+", max_age)[0]) if re.findall(r"\d+", max_age) else 120
            except Exception as e:
                print(f"Age parse failed for study: {study.get('title')} - {e}")
                min_age_val = 0
                max_age_val = 120

            # Participant age (must be a valid number)
            age = participant.get("age")
            if not isinstance(age, int):
                try:
                    age = int(age)
                except:
                    print(f"Invalid participant age: {age}. Defaulting to 0.")
                    age = 0

            if age is None or min_age_val is None or max_age_val is None:
                print(f"Skipping study due to invalid age comparison: {study.get('title')}")
                continue

            if not (min_age_val <= age <= max_age_val):
                print(f"Skipping due to age mismatch: {study.get('title')} (Allowed: {min_age_val}-{max_age_val}, Participant: {age})")
                continue

            # Score the match
            score = compute_score(study, participant_coords)
            if score < 0:
                continue

            # Build match object
            nct_id = study.get("nct_id", "")
            url = study.get("url") or (f"https://clinicaltrials.gov/ct2/show/{nct_id}" if nct_id else None)
            link = study.get("link", url)
            city = study.get("location", "Location N/A")
            title = study.get("title", "No Title")

            match = {
                "nct_id": nct_id,
                "title": title,
                "description": study.get("description", ""),
                "eligibility": study.get("eligibility", ""),
                "min_age": min_age,
                "max_age": max_age,
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
                "summary": f"{title} in {city}, recruiting ages {min_age} to {max_age}."
            }

            matched_studies.append(match)

        except Exception as e:
            print(f"Unhandled error processing study: {e}")
            continue

    return sorted(matched_studies, key=lambda x: x["match_score"], reverse=True)[:10]
