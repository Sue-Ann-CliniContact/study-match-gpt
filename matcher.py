
from utils import calculate_distance, format_study
import math

def match_studies(participant, studies):
    matched_studies = []
    user_age = participant.get("age")
    user_lat = participant.get("latitude")
    user_lon = participant.get("longitude")
    max_distance_km = 1000

    for study in studies:
        age_range = study.get("age_range", {})
        min_age = age_range.get("min", 0)
        max_age = age_range.get("max", 120)
        condition = study.get("condition", "").lower()

        if not (min_age <= user_age <= max_age):
            continue

        if "autism" not in condition:
            continue

        distance_km = None
        location = study.get("location")
        if location and user_lat is not None and user_lon is not None:
            study_lat = location.get("latitude")
            study_lon = location.get("longitude")
            if study_lat is not None and study_lon is not None:
                distance_km = calculate_distance(user_lat, user_lon, study_lat, study_lon)
                if distance_km > max_distance_km:
                    continue

        match_score = 8.0
        if distance_km is not None:
            if distance_km < 100:
                match_score += 1.5
            elif distance_km < 500:
                match_score += 0.5

        study["match_score"] = round(min(match_score, 10), 1)
        study["distance_km"] = distance_km
        matched_studies.append(study)

    matched_studies.sort(key=lambda s: s.get("match_score", 0), reverse=True)

    near_you = []
    national = []
    far_away = []

    for study in matched_studies:
        dist = study.get("distance_km")
        if dist is None:
            national.append(study)
        elif dist < 100:
            near_you.append(study)
        elif dist < 1000:
            national.append(study)
        else:
            far_away.append(study)

    def render_group(group_name, studies):
        if not studies:
            return ""
        section = f"
{group_name}:
"
        for i, s in enumerate(studies, 1):
            formatted = format_study(s)
            score = s.get("match_score", "N/A")
            section += f"{i}. {formatted}
Match Score: {score}/10

"
        return section

    grouped_output = "Here are some clinical studies that may be a fit:
"
    grouped_output += render_group("🔵 Near You", near_you)
    grouped_output += render_group("🟢 National", national)
    grouped_output += render_group("⚪ Far Away", far_away)

    return grouped_output.strip()
