
import re
import difflib

def extract_age_number(value):
    """Extract the first integer from a string like '3 Years'."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r"\d+", value)
        if match:
            return int(match.group())
    return None

def contains_autism_keyword(text, keywords):
    """Checks if text includes one of the autism-related keywords (exact or fuzzy)."""
    text = text.lower()
    for kw in keywords:
        if kw in text:
            return True
        if difflib.get_close_matches(kw, text.split(), n=1, cutoff=0.85):
            return True
    return False

def match_studies(participant_data, all_studies):
    matches = []

    age = participant_data.get("age") or participant_data.get("dob")
    location = participant_data.get("location", "").lower()
    diagnosis = participant_data.get("diagnosis", "").lower()
    study_focus = participant_data.get("study_age_focus", "").lower()

    autism_keywords = ["autism", "asd", "autism spectrum", "autism spectrum disorder", "autistic"]

    try:
        age = int(age)
    except:
        age = None

    for study in all_studies:
        title = study.get("title", "")
        eligibility = study.get("eligibility_criteria", "").lower()
        summary = study.get("brief_summary", "").lower() if study.get("brief_summary") else ""
        description = study.get("detailed_description", "").lower() if study.get("detailed_description") else ""
        condition = study.get("condition", "").lower() if study.get("condition") else ""
        min_age = extract_age_number(study.get("min_age"))
        max_age = extract_age_number(study.get("max_age"))
        cities = [loc.get("city", "").lower() for loc in study.get("locations", []) if loc.get("city")]
        zipcodes = [loc.get("zip", "").lower() for loc in study.get("locations", []) if loc.get("zip")]

        print("\n---")
        print("Evaluating study:", title)
        print("Condition:", condition)
        print("Eligibility:", eligibility)
        print("Cities:", cities)
        print("Zipcodes:", zipcodes)
        print("Min age:", min_age, "Max age:", max_age)

        searchable_text = f"{title.lower()} {condition} {eligibility} {summary} {description}"
        if not contains_autism_keyword(searchable_text, autism_keywords):
            print("❌ Skipped: No autism keyword found")
            continue

        if study_focus == "pediatric" and max_age and max_age > 18:
            print("❌ Skipped: Study not pediatric")
            continue
        if study_focus == "adult" and min_age and min_age < 18:
            print("❌ Skipped: Study not adult")
            continue

        if age is not None:
            if min_age is not None and age < min_age:
                print(f"❌ Skipped: Age {age} < min_age {min_age}")
                continue
            if max_age is not None and age > max_age:
                print(f"❌ Skipped: Age {age} > max_age {max_age}")
                continue

        if location:
            if not cities and not zipcodes:
                print("✅ MATCH (no location constraints)")
                matches.append(study)
                continue

            found = any(city in location for city in cities) or any(zipc in location for zipc in zipcodes)
            if not found:
                print("❌ Skipped: No matching location")
                continue

        print("✅ MATCH")
        matches.append({
            "title": title,
            "link": study.get("link", "No link provided"),
            "location": f"{study.get('location', '')}, {study.get('state', '')}, {study.get('country', '')}".strip(", "),
            "min_age": study.get("min_age"),
            "max_age": study.get("max_age"),
            "contact": f"{study.get('contact_name', 'N/A')} ({study.get('contact_email', 'N/A')})"
        })

    return matches
