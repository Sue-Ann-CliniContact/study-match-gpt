import math

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3958.8  # Radius of Earth in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def is_age_eligible(age, min_age, max_age):
    if age is None:
        return False
    if min_age is not None and age < min_age:
        return False
    if max_age is not None and age > max_age:
        return False
    return True

def score_match(study, participant_data):
    score = 0
    rationale = []

    # Location proximity
    participant_city = participant_data.get("location", "").lower()
    study_location = study.get("location", "").lower()
    if participant_city and study_location:
        if participant_city.split(",")[0] in study_location:
            score += 3
            rationale.append("Same city match")
        elif "united states" in study_location or "usa" in study_location or "us" in study_location:
            score += 2
            rationale.append("National match")
        else:
            rationale.append("International or unknown location")

    # Age eligibility scoring
    age = participant_data.get("age")
    min_age = study.get("min_age")
    max_age = study.get("max_age")

    if is_age_eligible(age, min_age, max_age):
        score += 2
        rationale.append(f"Age range {min_age if min_age is not None else '?'}-{max_age if max_age is not None else '?'}")
    else:
        rationale.append("Age outside study range")

    # Autism keyword already filtered at indexing stage
    score += 1
    rationale.append("Autism relevance")

    # Remote support
    if study.get("remote", False):
        score += 1
        rationale.append("Remote participation supported")

    # Comorbidities match
    participant_co_conditions = participant_data.get("co_conditions", "").lower()
    eligibility_text = study.get("eligibility", "").lower()
    comorbidity_terms = ["adhd", "anxiety", "epilepsy", "seizure", "intellectual disability"]

    if any(term in eligibility_text for term in comorbidity_terms):
        if any(term in participant_co_conditions for term in comorbidity_terms):
            score += 1
            rationale.append("Comorbidity match")
        else:
            rationale.append("Comorbidity mentioned but not participant match")

    return score, rationale

def match_studies(participant_data, studies, top_n=10):
    matches = []

    for study in studies:
        if study.get("status", "").lower() != "recruiting":
            continue

        score, rationale = score_match(study, participant_data)

        if score > 0:
            matches.append({
                "title": study.get("title", "No Title"),
                "location": study.get("location", "Unknown"),
                "link": study.get("link", ""),
                "summary": study.get("summary", "No summary."),
                "eligibility": study.get("eligibility", "Not provided"),
                "contact": study.get("contact", "Not available"),
                "match_score": f"{score}/10",
                "match_rationale": "; ".join(rationale)
            })

    matches.sort(key=lambda x: int(x["match_score"].split("/")[0]), reverse=True)
    return matches[:top_n]
