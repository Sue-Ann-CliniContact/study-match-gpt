def match_studies(participant_data, all_studies):
    matches = []

    # Extract key details from participant data
    age = participant_data.get("age") or participant_data.get("dob")  # fallback
    location = participant_data.get("location", "").lower()
    diagnosis = participant_data.get("diagnosis", "").lower()
    study_focus = participant_data.get("study_age_focus", "").lower()

    try:
        age = int(age)
    except:
        age = None

    for study in all_studies:
        title = study.get("title", "")
        eligibility = study.get("eligibility_criteria", "").lower()
        cities = [loc.get("city", "").lower() for loc in study.get("locations", []) if loc.get("city")]
        zipcodes = [loc.get("zip", "").lower() for loc in study.get("locations", []) if loc.get("zip")]
        min_age = study.get("min_age")
        max_age = study.get("max_age")
        condition = study.get("condition", "").lower()

        # Basic filters
        if "autism" not in condition and "autism" not in eligibility:
            continue

        if study_focus == "pediatric" and max_age and max_age > 18:
            continue
        if study_focus == "adult" and min_age and min_age < 18:
            continue

        if age is not None:
            if min_age and age < min_age:
                continue
            if max_age and age > max_age:
                continue

        # Location check
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
            if not found:
                continue

        matches.append(study)

    return matches
