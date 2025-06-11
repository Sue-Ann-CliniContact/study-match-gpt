import re
from utils import (
    is_autism_related,
    extract_age_range,
    extract_locations,
    is_within_distance,
    extract_participation_criteria,
    extract_comorbid_keywords,
    supports_remote_participation
)

def match_studies(participant_data, all_studies, top_n=10):
    matches = []

    user_age = participant_data.get("age")
    user_location = participant_data.get("location", "")
    co_conditions = participant_data.get("co_conditions", "").lower()
    preferred_visit = participant_data.get("visit_type", "").lower()

    for study in all_studies:
        # Skip completed studies
        if study.get("status", "").lower() == "completed":
            continue

        match_score = 0
        rationale = []

        # 1. Condition Relevance
        if is_autism_related(study):
            match_score += 2
            rationale.append("Autism relevance")

        # 2. Age Match
        min_age, max_age = extract_age_range(study)
        if min_age is not None and max_age is not None and user_age is not None:
            if min_age <= user_age <= max_age:
                match_score += 2
                rationale.append(f"Age range {min_age}-{max_age}")
            else:
                continue  # Age mismatch → skip
        else:
            rationale.append("No age criteria provided")

        # 3. Location Match
        locations = extract_locations(study)
        proximity = 0
        if locations:
            for loc in locations:
                score = is_within_distance(user_location, loc)
                proximity = max(proximity, score)
            if proximity > 0:
                match_score += proximity
                rationale.append(f"Proximity score {proximity}")
            else:
                rationale.append("National match")
        else:
            rationale.append("No location info")

        # 4. Comorbid Conditions Match
        if co_conditions and co_conditions != "no":
            crit_text = extract_participation_criteria(study)
            if extract_comorbid_keywords(co_conditions, crit_text):
                match_score += 1
                rationale.append("Comorbid condition match")

        # 5. Remote Study Support
        if preferred_visit in ["remote", "both"] and supports_remote_participation(study):
            match_score += 1
            rationale.append("Supports remote participation")

        matches.append({
            "study": study,
            "score": match_score,
            "rationale": "; ".join(rationale)
        })

    # Sort by score descending and return top_n
    sorted_matches = sorted(matches, key=lambda x: x["score"], reverse=True)
    return sorted_matches[:top_n]
