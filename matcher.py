import json
from geopy.distance import geodesic
import math

# Load the indexed studies once
with open("indexed_studies.json", "r", encoding="utf-8") as f:
    studies = json.load(f)

def calculate_distance(user_coords, study_location):
    try:
        return geodesic(user_coords, study_location).miles
    except:
        return None

def assess_match_score(study, data):
    score = 0
    reasons = []

    # Age match
    age = data.get("age")
    age_ok = study.get("eligibility", {}).get("min_age", 0) <= age <= study.get("eligibility", {}).get("max_age", 150)
    if age_ok:
        score += 3
        reasons.append("Age eligibility matched")
    else:
        reasons.append("Age not within range")

    # Diagnosis match
    diagnosis_keywords = ["autism", "asd", "autism spectrum"]
    if any(word in study.get("summary", "").lower() for word in diagnosis_keywords):
        score += 3
        reasons.append("Diagnosis criteria matched")

    # Location match
    user_location = data.get("location_coords")
    study_location = study.get("location_coords")
    if user_location and study_location:
        distance = calculate_distance(user_location, study_location)
        if distance is not None:
            if distance < 50:
                score += 3
                reasons.append("Study is nearby (<50 miles)")
            elif distance < 300:
                score += 2
                reasons.append("Study is within 300 miles")
            else:
                reasons.append("Study is distant (>300 miles)")
        else:
            reasons.append("Unable to calculate distance")
    else:
        reasons.append("Location not provided")

    return score, reasons

def match_studies(data):
    if not isinstance(data, dict):
        raise ValueError("Participant data must be a dictionary.")

    matches = []
    for study in studies:
        score, reasons = assess_match_score(study, data)
        matches.append({
            "name": study.get("title", "N/A"),
            "location": study.get("location", "Unknown"),
            "link": study.get("url"),
            "summary": study.get("summary", "No summary provided."),
            "eligibility": study.get("eligibility_text", "Not available."),
            "contact": study.get("contact", "Not listed"),
            "match_rationale": ", ".join(reasons),
            "match_score": round(score / 9 * 10, 1)
        })

    matches.sort(key=lambda x: -x["match_score"])

    # Grouped text output
    grouped_output = "Here are some clinical studies that may be a fit:
"
    for match in matches[:10]:
        grouped_output += (
            f"
📍 {match['name']}
"
            f"- Location: {match['location']}
"
            f"- Study Link: {match['link']}
"
            f"- Summary: {match['summary']}
"
            f"- Eligibility Overview: {match['eligibility']}
"
            f"- Contact: {match['contact']}
"
            f"- Match Score: {match['match_score']}/10
"
            f"- Match Rationale: {match['match_rationale']}
"
        )
    return grouped_output