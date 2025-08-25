import os
import json
from .vector_db_agent import VectorDBAgent
from root_agent.utils.preferences import PreferencesUtil

# Base path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SERVICENOW_DATA_PATH = os.path.join(BASE_DIR, "data", "servicenow", "incidents.json")
FLATTENED_PATH = os.path.join(BASE_DIR, "data", "servicenow", "incidents_flat.json")

print(f"ServiceNow tool loading data from: {SERVICENOW_DATA_PATH}")
print(f"File exists: {os.path.exists(SERVICENOW_DATA_PATH)}")

# Load and flatten incidents from all teams/projects
def load_flattened_incidents(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_incidents = []
    for entry in data:
        incidents = entry.get("incidents", [])
        for inc in incidents:
            # Optionally add team/project info to incident metadata
            inc["team"] = entry.get("team")
            inc["project"] = entry.get("project")
            all_incidents.append(inc)
    return all_incidents

flattened_incidents = load_flattened_incidents(SERVICENOW_DATA_PATH)
with open(FLATTENED_PATH, "w", encoding="utf-8") as f:
    json.dump({"incidents": flattened_incidents}, f, indent=2)

# Formatter for embedding
def servicenow_text_formatter(inc):
    steps = "\n".join([f"- {step}" for step in inc.get("steps_followed", [])])
    comments = "\n".join(
        f"- {c['commented_by']} ({c['role']}): {c['comment']} [{c.get('timestamp', '')}]"
        for c in inc.get("comment_history", [])
    )
    linked = "\n".join(f"- {r['type']} ({r['id']}): {r['url']}" for r in inc.get("linked_resources", []))
    details = [
        f"ID: {inc.get('id')}",
        f"Title: {inc.get('title', '')}",
        f"Description: {inc.get('description', '')}",
        f"Status: {inc.get('status', '')}",
        f"Importance: {inc.get('importance', '')}",
        f"Created At: {inc.get('created_at', '')}",
        f"Resolved At: {inc.get('resolved_at', '')}",
        f"Created By: {inc.get('created_by', {}).get('name', '')} ({inc.get('created_by', {}).get('role', '')})",
        f"Resolved By: {inc.get('resolved_by', {}).get('name', '') if inc.get('resolved_by') else ''}",
        f"Root Cause: {inc.get('root_cause', '')}",
        f"Resolution: {inc.get('resolution', '')}",
        f"Steps Followed:\n{steps}",
        f"Comments:\n{comments}",
        f"Linked Resources:\n{linked}"
    ]
    return "\n".join(details)

# Initialize the vector DB agent
servicenow_agent = VectorDBAgent(
    json_path=FLATTENED_PATH,          # Path to the flattened JSON
    json_list_key="incidents",         # Key inside the JSON file to extract incidents
    collection_name="servicenow_incidents",
    persist_dir="chroma_store/chroma_servicenow",
    text_formatter=servicenow_text_formatter
)

# Query function
def fetch_servicenow_incidents(query: str, k: int = 3):
    """
    Multi-tool Incident Search Prompt:

    When a user provides an incident number, title, or related query, search not only in ServiceNow but also across all selected tools (Jira, GitHub, Confluence, etc.) to gather comprehensive context.

    For example, if the user asks about "INC-9101":
    - Search ServiceNow for incident details, root cause, resolution, steps, comments, and linked resources.
    - Search Jira for related tickets, epics, bugs, or tasks that reference the incident or its systems.
    - Search GitHub for pull requests, discussions, or files that mention the incident, its fixes, or related code changes.
    - Search Confluence for documentation, runbooks, or pages that describe the incident, its impact, or team actions.

    Return a unified summary that includes:
    - Incident details from ServiceNow.
    - Related tickets/issues from Jira.
    - Relevant PRs/discussions/files from GitHub.
    - Supporting documentation from Confluence.
    - Any cross-references or links between tools.

    This enables users to get a full picture of the incident, its resolution, and all related activities across your engineering stack.

    Example usage:
        fetch_servicenow_incidents("INC-9101")
        fetch_servicenow_incidents("Why did the Flight Status API go down?")
    """

    results = servicenow_agent.query(query, top_k=k)
    formatted = []
    for r in results:
        formatted.append({
            "score": r["score"],
            "incident_summary": r["text"],
            "metadata": r["metadata"],
        })
    return formatted
    return formatted
