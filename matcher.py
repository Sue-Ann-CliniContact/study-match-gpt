import re
from geopy.distance import geodesic

def is_autism_related(text: str) -> bool:
    keywords = ["autism", "autistic", "asd", "spectrum disorder"]
    tl = text.lower()
    return any(k in tl for k in keywords)

def compute_score(study: dict, user_loc: tuple) -> int:
    score = 0
    # Condition relevance
    combined = (study.get("condition_summary", "") or "") + " " + (study.get("eligibility", "") or "")
    if is_autism_related(combined):
        score += 5

    # Age match is already filtered in main

    # Distance scoring
    study_city = study.get("location", "")
    study_coords = None
    # Map known cities (you can expand this to a map or geocoder)
    city = study_city.lower()
    if "dallas" in city:
        study_coords = (32.7767, -96.7970)
    elif "boston" in city:
        study_coords = (42.3601, -71.0589)
    elif "bethesda" in city:
        study_coords = (38.9847, -77.0947)
    elif "new york" in city:
        study_coords = (40.7128, -74.0060)
    # ... else fallback omitted

    dist = None
    if user_loc and study_coords:
        dist = geodesic(user_loc, study_coords).miles

    if dist is not None:
        if dist <= 50:
            score += 3
        elif dist <= 300:
            score += 2
        else:
            score += 1

    return score

def match_studies(participant: dict, studies: list) -> list:
    """
    Returns a list of up to 10 match dicts:
    {
      title, location, url, summary, eligibility, contact_name,
      contact_email, contact_phone, match_score, match_reason
    }
    """
    user_loc = participant.get("location")  # tuple (lat, lon)
    user_age = participant.get("age", 0)
    pediatric_only = participant.get("pediatric_only", True)

    matches = []
    for s in studies:
        # Age filter
        try:
            min_a = int(re.findall(r"\\d+", s.get("min_age", "0"))[0])
            max_a = int(re.findall(r"\\d+", s.get("max_age", "120"))[0])
        except:
            min_a, max_a = 0, 120
        if pediatric_only and max_a > 18:
            continue
        if not (min_a <= user_age <= max_a):
            continue

        # Compute score
        sc = compute_score(s, user_loc)
        if sc <= 0:
            continue

        # Build match
        match = {
            "title": s.get("title") or s.get("brief_title") or "No Title",
            "location": f"{s.get('location')}, {s.get('state')}",
            "url": s.get("url") or f"https://clinicaltrials.gov/ct2/show/{s.get('nct_id','')}",
            "summary": s.get("brief_summary") or s.get("description","No summary"),
            "eligibility": s.get("eligibility","Not provided"),
            "contact_name": s.get("contact_name","Not available"),
            "contact_email": s.get("contact_email","Not available"),
            "contact_phone": s.get("contact_phone","Not available"),
            "match_score": sc,
            "match_reason": [
                "Autism relevance" if is_autism_related((s.get("condition_summary","")+" "+s.get("eligibility","")).lower()) else "",
                f"Within age range {min_a}-{max_a}",
                f"Distance score: {sc-5-3 if sc>8 else sc-5}"  # simplistic rationale
            ]
        }
        matches.append(match)

    # Sort by score desc
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches[:10]
