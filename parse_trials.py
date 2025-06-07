import os
import xml.etree.ElementTree as ET

def extract_trial_data(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        def get_text(tag):
            el = root.find(tag)
            return el.text.strip() if el is not None and el.text else None

        # Extract key fields
        nct_id = get_text('id_info/nct_id')
        title = get_text('brief_title')
        conditions = [cond.text for cond in root.findall('condition') if cond.text]
        summary = get_text('brief_summary/textblock')
        eligibility = get_text('eligibility/criteria/textblock')
        min_age = get_text('eligibility/minimum_age')
        max_age = get_text('eligibility/maximum_age')
        location_elements = root.findall('location/facility/address')
        locations = [f"{el.findtext('city', '')}, {el.findtext('state', '')}" for el in location_elements]

        return {
            "nct_id": nct_id,
            "title": title,
            "conditions": conditions,
            "summary": summary,
            "eligibility": eligibility,
            "min_age": min_age,
            "max_age": max_age,
            "locations": list(set(locations))
        }
    except Exception as e:
        print(f"Failed to parse {xml_path}: {e}")
        return None

def find_autism_trials(data_dir, max_trials=100):
    results = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.xml'):
                path = os.path.join(root, file)
                trial = extract_trial_data(path)
                if trial and any("autism" in cond.lower() for cond in trial["conditions"]):
                    results.append(trial)
                if len(results) >= max_trials:
                    return results
    return results

if __name__ == "__main__":
    xml_dir = "./data/ctg-public-xml"
    autism_trials = find_autism_trials(xml_dir, max_trials=50)

    for trial in autism_trials:
        print(f"\n📌 {trial['title']} ({trial['nct_id']})")
        print(f"  Conditions: {trial['conditions']}")
        print(f"  Locations: {trial['locations']}")
        print(f"  Age Range: {trial['min_age']} – {trial['max_age']}")
        print(f"  Eligibility: {trial['eligibility'][:200]}...\n")
