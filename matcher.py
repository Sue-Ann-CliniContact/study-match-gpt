import re

def extract_age_number(value):
    """Extracts the first number from a string like '5 Years' or returns the int directly."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r"\d+", value)
        if match:
            return int(match.group())
    return None

def match_studies(participant_data, all_studies):
    matches = []

    # Extract key details from participant data
    age = participant_data.get("age") or participant_data.get("dob")  # fallback
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
        cities = [loc.get("city", "").lower() for loc in study.get("locations", []) if loc.get("city")]
        zipcodes = [loc.get("zip", "").lower() for loc in study.get("locations", []) if loc.get("zip")]
        min_age = extract_age_number(study.get("min_age"))
        max_age = extract_age_number(study.get("max_age"))
        condition = study.get("condition", "").lower()

        print("\n---")
        print("Evaluating study:", title)
        print("Condition:", condition)
        print("Eligibility:", eligibility)
        print("Cities:", cities)
        print("Zipcodes:", zipcodes)
        print("Min age:", min_age, "Max age:", max_age)

        # ✅ Check for autism keyword in any searchable field
        searchable_text = f"{title.lower()} {condition} {eligibility}"
        if not any(keyword in searchable_text for keyword in autism_keywords):
            print("❌ Skipped: No autism keyword found")
            continue

        # ✅ Pediatric/adult study focus filter
        if study_focus == "pediatric" and max_age and max_age > 18:
            print("❌ Skipped: Study not pediatric")
            continue
        if study_focus == "adult" and min_age and min_age < 18:
            print("❌ Skipped: Study not adult")
            continue

        # ✅ Age eligibility check
        if age is not None:
            if min_age is not None and age < min_age:
                print(f"❌ Skipped: Age {age} < min_age {min_age}")
                continue
            if max_age is not None and age > max_age:
                print(f"❌ Skipped: Age {age} > max_age {max_age}")
                continue

        # ✅ Location matching (loose match in city or zip)
        if location:
            found = False
            for city in cities:
                if city and city in location:
                    found = True
                    break
            for zipc in zipcodes:
                if zipc and zipc in location:
                    found = True
                    break
            if not found and cities:
                print("❌ Skipped: No matching location")
                continue

        print("✅ MATCH")
        matches.append(study)

    return matches
