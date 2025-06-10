
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

def calculate_age(birth_date_str):
    try:
        birth_date = datetime.strptime(birth_date_str, "%B %d, %Y")
        today = datetime.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except Exception:
        return None

def haversine_distance_km(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0

    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def format_matches_for_gpt(matches):
    if not matches:
        return (
            "Unfortunately, no studies matched based on your details. "
            "Would you like us to follow up if new ones become available?"
        )

    output = "Here are some clinical studies that may be a fit:\n\n"
    for idx, study in enumerate(matches, 1):
        reasons = study.get('match_reason', [])
        rationale = "; ".join(reasons) if reasons else 'No specific rationale provided.'

        output += f"**{idx}. {study['title']}**\n"
        output += f"- **Location**: {study['location']}, {study['state']}\n"
        output += f"- **Study Link**: [View Study]({study['url']})\n"
        output += f"- **Summary**: {study['summary']}\n"
        output += (
            f"- **Eligibility Overview**: {study['eligibility'] or 'Not provided'}\n"
        )
        output += (
            f"- **Contact**: {study['contact_name']} | {study['contact_email']} | {study['contact_phone']}\n"
        )
        output += f"- **Match Rationale**: {rationale}\n\n"

    return output
