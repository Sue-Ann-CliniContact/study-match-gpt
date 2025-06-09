
def match_studies(user, studies):
    results = []
    for study in studies:
        if "autism" not in study["conditions"].lower():
            continue
        if not study["eligibility"]["min_age"] <= user["age"] <= study["eligibility"]["max_age"]:
            continue
        if user["location"].lower() not in study["locations"].lower():
            continue
        results.append({
            "title": study["title"],
            "criteria": study["eligibility"],
            "contact": study.get("contact"),
            "location": study.get("locations"),
            "nct_id": study["nct_id"],
            "url": f"https://clinicaltrials.gov/study/{study['nct_id']}"
        })
    return results[:5]
