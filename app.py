import os
import zipfile
import xml.etree.ElementTree as ET
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
ZIP_URL = "https://drive.google.com/uc?export=download&id=1T6MnvF_XpFwNpOQNql-or931Bx48b5Jj"
ZIP_PATH = "ctg-public-xml.zip"
EXTRACT_DIR = "data/ctg-public-xml"
AUTISM_TERMS = ["autism", "autistic", "ASD", "autism spectrum disorder", "pervasive developmental disorder"]

# 1. Ensure local dataset
def ensure_dataset():
    if not os.path.exists(EXTRACT_DIR):
        print("Downloading and extracting dataset...")
        zip_response = requests.get(ZIP_URL)
        with open(ZIP_PATH, "wb") as f:
            f.write(zip_response.content)
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)

# 2. Check if trial matches autism-related content
def is_autism_study(texts: List[str]) -> bool:
    text = " ".join([t.lower() for t in texts if t])
    return any(term in text for term in AUTISM_TERMS)

# 3. Parse trials from XML
def parse_trials(age: int, state: str) -> List[dict]:
    matches = []
    for root_dir, _, files in os.walk(EXTRACT_DIR):
        for file in files:
            if not file.endswith(".xml"):
                continue
            path = os.path.join(root_dir, file)
            try:
                tree = ET.parse(path)
                root = tree.getroot()
                nct_id = root.findtext("id_info/nct_id")
                title = root.findtext("brief_title")
                summary = root.findtext("brief_summary/textblock")
                elig = root.find("eligibility")
                locs = root.findall("location/facility/address/state")
                criteria = elig.findtext("criteria/textblock") if elig is not None else ""
                min_age = elig.findtext("minimum_age") if elig is not None else ""
                max_age = elig.findtext("maximum_age") if elig is not None else ""

                def parse_age(age_str):
                    if not age_str or "N/A" in age_str:
                        return None
                    num, unit = age_str.split()
                    return int(num) * (12 if "year" in unit else 1)

                min_months = parse_age(min_age)
                max_months = parse_age(max_age)
                age_months = age * 12
                age_ok = (
                    (min_months is None or age_months >= min_months) and
                    (max_months is None or age_months <= max_months)
                )

                state_matches = any(state.lower() in (l.text or "").lower() for l in locs)

                if is_autism_study([title, summary, criteria]) and age_ok and state_matches:
                    matches.append({
                        "nct_id": nct_id,
                        "title": title,
                        "summary": summary,
                        "eligibility": criteria,
                        "location_states": [l.text for l in locs if l.text],
                        "score": int(age_ok) + int(state_matches)
                    })

                if len(matches) >= 5:
                    return sorted(matches, key=lambda x: -x["score"])[:5]

            except Exception:
                continue
    return sorted(matches, key=lambda x: -x["score"])[:5]

# 4. Live API endpoint
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    history = data.get("history", [])
    age, state = None, None

    # Extract age and state from conversation history
    for turn in history + [{"role": "user", "content": message}]:
        msg = turn["content"].lower()
        if not age and any(x in msg for x in ["age", "years old"]):
            for word in msg.split():
                if word.isdigit():
                    age = int(word)
                    break
        if not state and any(s in msg for s in ["i live in", "from", "based in"]):
            state = msg.split()[-1].title()

    if age and state:
        ensure_dataset()
        results = parse_trials(age, state)
        if results:
            reply = "**Here are some matching studies:**\n\n"
            for r in results:
                reply += f"**{r['title']}**\n[Study Link](https://clinicaltrials.gov/study/{r['nct_id']})\nLocation(s): {', '.join(r['location_states'])}\n\n"
            return {"reply": reply}
        else:
            return {"reply": "I searched but didn’t find any matching studies yet. You can try adjusting the criteria or ask for help."}
    else:
        return {"reply": "Please tell me your age and the state or city where you're located so I can search relevant studies."}

