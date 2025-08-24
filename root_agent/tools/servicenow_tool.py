# tools/servicenow_tool.py

import json
import os

def fetch_servicenow_incidents(query: str):
    print(f"🔍 fetch_servicenow_incidents called with query: '{query}'")
    """Mock tool: fetch ServiceNow incidents from a local JSON file."""
    json_path = r"C:\Users\HAG047\OneDrive - Maersk Group\Documents\msk-cargo-quest-navo\navo-backend\maersk-projects\Team001\project001\servicenow.json"
    
    if not os.path.exists(json_path):
        print("❌ ServiceNow JSON not found.")
        return {"error": "ServiceNow JSON not found."}

    with open(json_path, "r", encoding="utf-8") as f:
        incidents = json.load(f).get("incidents", [])

    # If a query is provided, do simple filter
    if query:
        filtered = [i for i in incidents if query.lower() in (i.get("title", "") + i.get("description", "")).lower()]
    else:
        filtered = incidents

    # Return top 3 results
    return filtered[:3]
