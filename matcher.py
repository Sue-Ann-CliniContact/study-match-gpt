
import json
import re

def is_autism_related(text):
    autism_keywords = ["autism", "autistic", "ASD", "spectrum disorder"]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in autism_keywords)

def match_studies(participant, studies):
    matched_studies = []
    for study in studies:
        try:
            condition = study.get("condition_summary", "") or ""
            eligibility = study.get("eligibility", "") or ""
            combined_text = condition + " " + eligibility

            if not is_autism_related(combined_text):
                print(f"❌ Skipped: No autism keyword found")
                continue

            min_age = study.get("min_age", "N/A")
            max_age = study.get("max_age", "N/A")
            try:
                min_age_val = int(re.findall(r"\d+", min_age)[0]) if min_age != "N/A" else 0
                max_age_val = int(re.findall(r"\d+", max_age)[0]) if max_age != "N/A" else 120
            except:
                min_age_val = 0
                max_age_val = 120

            age = participant.get("age", 0)
            if not (min_age_val <= age <= max_age_val):
                print(f"❌ Skipped: Age {age} not in range {min_age_val}-{max_age_val}")
                continue

            location = participant.get("location", "").lower()
            study_location = (
                study.get("location", "") or ""
            ).lower()
            if location and location not in study_location:
                print(f"⚠️ Location mismatch: {location} not in {study_location}")

            match = {
                "nct_id": study.get("nct_id", ""),
                "title": study.get("title", ""),
                "description": study.get("description", ""),
                "eligibility": study.get("eligibility", ""),
                "min_age": study.get("min_age", ""),
                "max_age": study.get("max_age", ""),
                "location": study.get("location", ""),
                "state": study.get("state", ""),
                "country": study.get("country", ""),
                "status": study.get("status", ""),
                "link": study.get("link", "Not available"),
                "contact_name": study.get("contact_name", "Not available"),
                "contact_email": study.get("contact_email", "Not available"),
                "contact_phone": study.get("contact_phone", "Not available"),
            }
            matched_studies.append(match)
        except Exception as e:
            print(f"Error processing study: {e}")
            continue
    return matched_studies
