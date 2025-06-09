
import re

def match_studies(participant, studies):
    age = int(participant.get("age", 0))
    location = participant.get("location", "").lower()
    diagnosis = participant.get("diagnosis", "").lower()

    results = []
    for study in studies:
        if "autism" not in study.get("Conditions", "").lower():
            continue

        age_range = study.get("Eligibility", {}).get("MinimumAge", "") + " - " + study.get("Eligibility", {}).get("MaximumAge", "")
        if "years" in age_range.lower():
            min_age_match = re.search(r"(\d+)", study.get("Eligibility", {}).get("MinimumAge", ""))
            max_age_match = re.search(r"(\d+)", study.get("Eligibility", {}).get("MaximumAge", ""))
            if min_age_match and max_age_match:
                min_age = int(min_age_match.group(1))
                max_age = int(max_age_match.group(1))
                if not (min_age <= age <= max_age):
                    continue

        results.append({
            "brief_title": study.get("BriefTitle", ""),
            "status": study.get("OverallStatus", ""),
            "location": study.get("LocationFacility", ""),
            "link": study.get("NCTLink", ""),
            "eligibility": study.get("EligibilityCriteria", "")
        })

    return results[:5]
