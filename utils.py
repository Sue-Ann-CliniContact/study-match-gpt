from datetime import datetime
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="heytrial-matcher")

def extract_participant_data(chat_history):
    if not isinstance(chat_history, list):
        raise ValueError("Chat history must be a list")

    info = {}
    for msg in chat_history:
        if isinstance(msg, dict) and msg.get("role") == "user":
            text = msg.get("content", "").lower()
            if "date of birth" in text or "born" in text:
                dob_str = text.split("born")[-1].strip() if "born" in text else text.split("birth is")[-1].strip()
                try:
                    dob = datetime.strptime(dob_str, "%B %d, %Y")
                    age = (datetime.now() - dob).days // 365
                    info["age"] = age
                except:
                    pass
            if "we live in" in text:
                location = text.split("we live in")[-1].split(".")[0].strip()
                info["location"] = location
                try:
                    loc = geolocator.geocode(location)
                    if loc:
                        info["location_coords"] = (loc.latitude, loc.longitude)
                except:
                    pass
            if "diagnosed with autism" in text or "has autism" in text:
                info["diagnosed"] = True
            if "she is verbal" in text or "he is verbal" in text:
                info["verbal"] = True

    return info