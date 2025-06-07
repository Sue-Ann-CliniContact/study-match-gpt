import os
import xml.etree.ElementTree as ET

AUTISM_TERMS = ["autism", "autistic", "asd", "autism spectrum disorder", "autistic traits"]

def match_trials(condition, age, location_hint):
    matched = []
    trials_path = os.getenv("XML_DIR", "nct_data")  # Folder of XMLs
    for fname in os.listdir(trials_path):
        if not fname.endswith(".xml"):
            continue
        try:
            tree = ET.parse(os.path.join(trials_path, fname))
            root = tree.getroot()
            title = root.findtext("brief_title", "")
            summary = root.findtext("brief_summary/textblock", "")
            criteria = root.findtext("eligibility/criteria/textblock", "")
            locations = [l.findtext("facility/address/city", "") for l in root.findall("location")]
            min_age = root.findtext("eligibility/minimum_age", "N/A")
            max_age = root.findtext("eligibility/maximum_age", "N/A")
            conds = [c.text for c in root.findall("condition")]

            # Normalize and check match
            fulltext = f"{title} {summary} {criteria} {' '.join(conds)}".lower()
            if not any(term in fulltext for term in AUTISM_TERMS):
                continue

            # Age filtering
            def parse_age(a):
                if "year" in a:
                    return int(a.split()[0])
                elif "month" in a:
                    return int(int(a.split()[0]) / 12)
                return 0
            if "N/A" in min_age or "N/A" in max_age:
                continue
            if not (parse_age(min_age) <= age <= parse_age(max_age)):
                continue

            # Scoring
            loc_match = any(location_hint.lower() in l.lower() for l in locations)
            score = 1
            if loc_match:
                score += 1

            matched.append({
                "title": title,
                "criteria": (criteria[:300] + "...") if criteria else "See full link.",
                "location": locations[0] if locations else "Not listed",
                "age_range": f"{min_age} - {max_age}",
                "url": f"https://clinicaltrials.gov/study/{fname.replace('.xml', '')}",
                "score": score
            })
        except Exception:
            continue
    return sorted(matched, key=lambda x: -x["score"])[:5]
