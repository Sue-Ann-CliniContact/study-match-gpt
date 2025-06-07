import os
import xml.etree.ElementTree as ET

AUTISM_TERMS = [
    "autism", "autism spectrum", "asd", "autistic traits", "autism spectrum disorder"
]

def extract_trial_data(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        def get_text(tag):
            el = root.find(tag)
            return el.text.strip() if el is not None and el.text else None

        def get_ages():
            min_age = get_text('eligibility/minimum_age')
            max_age = get_text('eligibility/maximum_age')
            return (
                int(min_age.split()[0]) if min_age and "Years" in min_age else 0,
                int(max_age.split()[0]) if max_age and "Years" in max_age else 99
            )

        locations = []
        for loc in root.findall('location/facility/address'):
            city = loc.findtext('city', '')
            state = loc.findtext('state', '')
            locations.append(f"{city}, {state}".strip())

        return {
            "nct_id": get_text("id_info/nct_id"),
            "title": get_text("brief_title"),
            "summary": get_text("brief_summary/textblock"),
            "eligibility": get_text("eligibility/criteria/textblock"),
            "conditions": [c.text.lower() for c in root.findall("condition") if c.text],
            "min_age": get_ages()[0],
            "max_age": get_ages()[1],
            "locations": list(set(locations))
        }
    except Exception as e:
        print(f"Failed to parse {xml_path}: {e}")
        return None

def match_trials(xml_dir, user_age=0, location_hint=None, limit=5):
    matched = []
    for root_dir, _, files in os.walk(xml_dir):
        for fname in files:
            if not fname.endswith(".xml"):
                continue
            trial = extract_trial_data(os.path.join(root_dir, fname))
            if not trial:
                continue

            content_to_search = (
                " ".join(trial["conditions"]) + " " +
                (trial["summary"] or "") + " " +
                (trial["eligibility"] or "") + " " +
                (trial["title"] or "")
            ).lower()

            if not any(term in content_to_search for term in AUTISM_TERMS):
                continue

            if not (trial["min_age"] <= user_age <= trial["max_age"]):
                continue

            trial["score"] = 1
            if location_hint and any(location_hint.lower() in loc.lower() for loc in trial["locations"]):
                trial["score"] += 1

            matched.append(trial)

    sorted_trials = sorted(matched, key=lambda x: -x["score"])
    return sorted_trials[:limit]
