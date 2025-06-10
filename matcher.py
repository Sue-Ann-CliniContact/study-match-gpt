
import math
from utils import (
    calculate_age,
    haversine_distance,
    normalize_text,
    extract_zip_and_state
)

def match_studies(participant_data, studies):
    matched_studies = []
    participant_zip = participant_data.get("zip_code", "")
    participant_state = participant_data.get("state", "")
    participant_lat = participant_data.get("latitude")
    participant_lon = participant_data.get("longitude")
    participant_age = participant_data.get("age")
    diagnosis = normalize_text(participant_data.get("diagnosis", ""))
    verbal = participant_data.get("verbal", "").lower()
    co_conditions = normalize_text(participant_data.get("co_conditions", ""))
    mobility = participant_data.get("mobility", "").lower()
    schooling = normalize_text(participant_data.get("schooling", ""))
    pediatric_only = participant_data.get("pediatric_only", True)

    for study in studies:
        age_match = False
        condition_match = False
        location_score = 0
        summary = study.get("summary", "").lower()
        eligibility = study.get("eligibility", "").lower()
        inclusion = study.get("inclusion_criteria", "").lower()
        exclusion = study.get("exclusion_criteria", "").lower()
        location = study.get("location", "")
        zip_match = participant_zip in location
        state_match = participant_state in location

        # Age filtering
        min_age = study.get("min_age")
        max_age = study.get("max_age")
        if min_age is not None and max_age is not None:
            age_match = min_age <= participant_age <= max_age

        # Pediatric preference filter
        if pediatric_only and max_age is not None and max_age > 18:
            continue  # Skip adult studies

        # Diagnosis match
        if "autism" in summary or "asd" in summary or "autism" in eligibility:
            condition_match = True

        # Score based on distance
        study_lat = study.get("latitude")
        study_lon = study.get("longitude")
        distance = None
        if participant_lat and participant_lon and study_lat and study_lon:
            distance = haversine_distance(participant_lat, participant_lon, study_lat, study_lon)
            if distance <= 50:
                location_score = 10
            elif distance <= 250:
                location_score = 7
            else:
                location_score = 4
        else:
            if zip_match:
                location_score = 10
            elif state_match:
                location_score = 7
            else:
                location_score = 4

        score = 0
        if condition_match:
            score += 10
        if age_match:
            score += 10
        score += location_score

        match = {
            "name": study.get("name"),
            "location": study.get("location"),
            "link": study.get("link"),
            "summary": study.get("summary"),
            "eligibility": study.get("eligibility"),
            "contact": study.get("contact"),
            "distance": distance,
            "score": score
        }
        matched_studies.append(match)

    matched_studies.sort(key=lambda x: x["score"], reverse=True)

    near_you = []
    national = []
    other = []

    for study in matched_studies:
        dist = study["distance"]
        if dist is not None:
            if dist <= 50:
                near_you.append(study)
            elif dist <= 250:
                national.append(study)
            else:
                other.append(study)
        else:
            other.append(study)

    grouped_output = "Here are some clinical studies that may be a fit:\n\n"

    def format_group(title, group):
        section = f"**{title}**\n\n"
        for idx, study in enumerate(group, 1):
            section += (
                f"{idx}. {study['name']}\n"
                f"- Location: {study['location']}\n"
                f"- Study Link: {study['link']}\n"
                f"- Summary: {study['summary']}\n"
                f"- Eligibility Overview: {study['eligibility']}\n"
                f"- Contact: {study['contact']}\n"
                f"- Match Confidence Score: {study['score']}/30\n\n"
            )
        return section

    if near_you:
        grouped_output += format_group("🔵 Near You (≤50 miles)", near_you)
    if national:
        grouped_output += format_group("🟢 National (≤250 miles)", national)
    if other:
        grouped_output += format_group("⚪ Other (Unspecified/International)", other)

    return grouped_output.strip()
