# tools/jira_tool.py

import json
import os

# Path to your mock Jira issues JSON file
JIRA_DATA_PATH = r"C:\Users\HAG047\OneDrive - Maersk Group\Documents\msk-cargo-quest-navo\navo-backend\maersk-projects\Team001\project001\jira.json"

def fetch_jira_issues(query: str):
    print(f"🔍 fetch_jira_tickets called with query: '{query}'")
    """Mock tool to search Jira issues JSON for matches"""
    if not os.path.exists(JIRA_DATA_PATH):
        return {"status": "error", "message": "Jira mock data file not found"}

    with open(JIRA_DATA_PATH, "r") as f:
        issues = json.load(f)

    results = []
    for issue in issues:
        text = (
            issue.get("key", "") + " " +
            issue.get("summary", "") + " " +
            issue.get("description", "")
        ).lower()

        if query.lower() in text:
            results.append(issue)

    return {
        "status": "success",
        "results": results[:3]  # return top 3 matches
    }
