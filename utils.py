import math
from datetime import datetime
from dateutil import parser

def calculate_age(dob_str: str) -> int:
    """
    Given "July 4, 2013", returns integer age.
    """
    try:
        dob = parser.parse(dob_str).date()
        today = datetime.today().date()
        years = today.year - dob.year
        if (today.month, today.day) < (dob.month, dob.day):
            years -= 1
        return years
    except:
        return 0

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Returns distance in miles between two coords.
    """
    # Earth radius in miles
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def extract_participant_data(raw: dict) -> dict:
    """
    Normalize the raw JSON from the GPT extract stage into our participant dict.
    Expect raw contains keys: dob, location, pediatric_only, diagnosis, verbal, etc.
    """
    return {
        "age": raw.get("age", 0),
        "location": raw.get("location_coords"),  # GPT needs to supply this
        "pediatric_only": raw.get("study_age_focus","pediatric").lower().startswith("ped"),
        "diagnosis": raw.get("diagnosis"),
        "verbal": raw.get("verbal"),
        "email": raw.get("email"),
        "phone": raw.get("phone"),
        "relation": raw.get("relation"),
        "dob": raw.get("dob"),
        # any other fields you need downstream
    }

def format_matches_for_gpt(matches: list) -> str:
    """
    Given the list from match_studies(), render a markdown/text reply with
    grouped sections, match score, rationale, and all study details.
    """
    if not matches:
        return "Unfortunately, no studies matched based on your details."

    text = "Here are some clinical studies that may be a fit:\n\n"
    # You could group by score or distance here if desired
    for i, m in enumerate(matches, 1):
        text += (
            f"**{i}. {m['title']}**\n"
            f"- Location: {m['location']}\n"
            f"- Link: [View Study]({m['url']})\n"
            f"- Summary: {m['summary']}\n"
            f"- Eligibility: {m['eligibility']}\n"
            f"- Contact: {m['contact_name']} | {m['contact_email']} | {m['contact_phone']}\n"
            f"- Match Score: {m['match_score']}/10\n"
            f"- Match Rationale: {', '.join([r for r in m['match_reason'] if r])}\n\n"
        )
    return text.strip()
