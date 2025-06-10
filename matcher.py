
import re
from geopy.distance import geodesic


def is_autism_related(text):
    autism_keywords = ["autism", "autistic", "ASD", "spectrum disorder"]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in autism_keywords)


def get_distance_bucket(distance_miles):
    if distance_miles < 50:
        return "Near You"
    elif distance_miles < 200:
        return "In Your State"
    else:
        return "National"


def compute_match_score(study, participant_coords, participant_age):
    score = 0
    condition = study.get("condition_summary", "").lower()
    eligibility = study.get("eligibility", "").lower()

    # Base relevance if autism is mentioned
    if is_autism_related(f"{condition} {eligibility}"):
        score += 5

    # Country check
    if study.get("country", "") != "United States":
        return -1, "Excluded: Non-US Study"

    # Location distance
    study_coords = study.get("coordinates", None)
    distance_miles = 9999
    if study_coords and participant_coords:
        distance_miles = geodesic(participant_coords, study_coords).miles
        if distance_miles < 50:
            score += 3
        elif distance_miles < 200:
            score += 2
        elif distance_miles < 1000:
            score += 1

    # Age filtering
    try:
        min_age = int(study.get("min_age_years", -1))
        max_age = int(study.get("max_age_years", -1))
        if (min_age >= 0 and participant_age < min_age) or (max_age >= 0 and participant_age > max_age):
            return -1, "Excluded: Age not in range"
        else:
            score += 1
    except:
        pass

    confidence = round((score / 10) * 10, 1)  # Normalize to a 10-point scale
    return score, f"{confidence}/10 match based on age, condition, and proximity ({get_distance_bucket(distance_miles)})"


def match_studies(studies, participant_data):
    matched = []

    participant_coords = participant_data.get("coordinates", None)
    participant_age = participant_data.get("age", None)

    for study in studies:
        score, rationale = compute_match_score(study, participant_coords, participant_age)
        if score >= 0:
            matched.append({
                "study": study,
                "score": score,
                "match_rationale": rationale,
                "distance_bucket": get_distance_bucket(
                    geodesic(participant_coords, study["coordinates"]).miles
                    if participant_coords and "coordinates" in study else 9999
                )
            })

    # Sort by score descending
    return sorted(matched, key=lambda x: x["score"], reverse=True)
