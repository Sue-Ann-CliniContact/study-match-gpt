
import os
import requests

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
BOARD_ID = 1987448172
GROUP_ID = "topics"

COLUMN_MAPPING = {
    "name": "name",
    "email": "email_mkrjhbqe",
    "phone": "phone_mkrj1e0m",
    "dob": "text_mkrk7xqa",
    "location": "text_mkrjg9tz",
    "relation": "text_mkrkgtyt",
    "text_opt_in": "text_mkrknr35",
    "diagnosis": "text_mkrkh8qw",
    "diagnosis_age": "text_mkrkz666",
    "verbal": "text_mkrkm84b",
    "medications": "text_mkrke8tm",
    "medication_names": "text_mkrkzpxn",
    "co_conditions": "text_mkrkrxv3",
    "mobility": "text_mkrk547b",
    "school_program": "text_mkrkgdjj",
    "visit_type": "text_mkrkb1gp",
    "study_age_focus": "text_mkrk5kgn",
    "study_goals": "text_mkrjjyek"
}

def push_to_monday(participant_data):
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json"
    }

    # Prepare column values in Monday API format
    column_values = {}
    for key, column_id in COLUMN_MAPPING.items():
        if key in participant_data:
            column_values[column_id] = participant_data[key]

    # Construct the mutation query
    mutation = {
        "query": f'''
            mutation {{
                create_item (
                    board_id: {BOARD_ID},
                    group_id: "{GROUP_ID}",
                    item_name: "{participant_data.get("name", "New Participant")}",
                    column_values: "{json_escape(column_values)}"
                ) {{
                    id
                }}
            }}
        '''
    }

    response = requests.post(url, headers=headers, json=mutation)
    if response.status_code != 200:
        print("Error pushing to Monday:", response.text)
    return response.json()

def json_escape(data):
    import json
    return json.dumps(data).replace('"', '\"')
