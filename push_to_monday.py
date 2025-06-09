import os
import requests
import json

MONDAY_API_KEY = os.getenv("MONDAY_API_KEY")
MONDAY_BOARD_ID = 1987448172  # GPT - Autism
MONDAY_GROUP_ID = "topics"

def push_to_monday(participant_data):
    name = participant_data.get("name", "New GPT Lead")

    column_values = {
        "email_mkrjhbqe": participant_data.get("email"),
        "phone_mkrj1e0m": participant_data.get("phone"),
        "text_mkrk7xqa": participant_data.get("dob"),
        "text_mkrjg9tz": participant_data.get("location"),
        "text_mkrkgtyt": participant_data.get("relation_to_participant"),
        "text_mkrknr35": participant_data.get("text_opt_in"),
        "text_mkrkh8qw": participant_data.get("diagnosis"),
        "text_mkrkz666": participant_data.get("age_at_diagnosis"),
        "text_mkrkm84b": participant_data.get("verbal_status"),
        "text_mkrke8tm": participant_data.get("on_medication"),
        "text_mkrkzpxn": participant_data.get("medications"),
        "text_mkrkrxv3": participant_data.get("co_conditions"),
        "text_mkrk547b": participant_data.get("mobility"),
        "text_mkrkgdjj": participant_data.get("school_program"),
        "text_mkrkb1gp": participant_data.get("visit_preference"),
        "text_mkrk5kgn": participant_data.get("pediatric_or_adult"),
        "text_mkrjjyek": participant_data.get("goals")
    }

    column_values_str = json.dumps(column_values).replace('"', '\\"')

    mutation = f'''
    mutation {{
      create_item(
        board_id: {MONDAY_BOARD_ID},
        group_id: "{MONDAY_GROUP_ID}",
        item_name: "{name}",
        column_values: "{column_values_str}"
      ) {{
        id
      }}
    }}
    '''

    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.monday.com/v2",
        headers=headers,
        json={"query": mutation}
    )

    if response.status_code != 200:
        print("Error pushing to Monday:", response.text)
        return False

    data = response.json()
    if "errors" in data:
        print("Error pushing to Monday:", data)
        return False

    return True

