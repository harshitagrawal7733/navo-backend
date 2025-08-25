import os
import json
from .vector_db_agent import VectorDBAgent
from root_agent.utils.preferences import PreferencesUtil

# Use absolute path to ensure correct file loading
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
JIRA_DATA_PATH = os.path.join(BASE_DIR, "data", "jira", "all_issues.json")
FLATTENED_PATH = os.path.join(BASE_DIR, "data", "jira", "all_issues_flat.json")

# Debug: Print the path being used
print(f"Jira tool loading data from: {JIRA_DATA_PATH}")
print(f"File exists: {os.path.exists(JIRA_DATA_PATH)}")

def get_all_issues():
    if not os.path.exists(JIRA_DATA_PATH):
        return []
    with open(JIRA_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_issues = []
        for k in ['epics', 'stories', 'bugs', 'tasks']:
            all_issues.extend(data.get(k, []))
        return all_issues

flattened_issues = get_all_issues()
with open(FLATTENED_PATH, 'w', encoding='utf-8') as f:
    json.dump({"issues": flattened_issues}, f, ensure_ascii=False, indent=2)

def jira_text_formatter(issue):
    details = [
        f"Key: {issue.get('id', issue.get('key', ''))}",
        f"Title: {issue.get('title', issue.get('summary', ''))}",
        f"Status: {issue.get('status', '')}",
        f"Assignee: {issue.get('assignee', '')}",
        f"Description: {issue.get('description', '')}",
        f"Type: {issue.get('type', '')}",
        f"Created At: {issue.get('created_at', '')}",
        f"Reporter: {issue.get('reporter', '')}",
        f"Priority: {issue.get('priority', '')}"
    ]
    # Add comments if present
    if 'comments' in issue and issue['comments']:
        comments = "\n".join([f"- {c.get('author', '')}: {c.get('body', '')}" for c in issue['comments']])
        details.append(f"Comments:\n{comments}")
    return "\n".join(details)

jira_agent = VectorDBAgent(
    json_path=FLATTENED_PATH,
    collection_name="jira_issues",
    persist_dir="chroma_store/chroma_jira",
    json_list_key="issues",
    text_formatter=jira_text_formatter
)

def fetch_jira_issues(query: str, k: int = 3):
    """
    User Intent:
    - Return up to 'k' Jira issues based on user query.
    - If fewer than 'k' results are found, inform the user how many were found.
    - Provide detailed information for each issue, including key, title, status, assignee, description, and any relevant metadata.
    - If the user asks for a specific type (e.g., "all bugs"), return all matching issues.
    - If no results are found, apologize and suggest possible follow-up queries.

    Example:
        "Bring me any 5 results from Jira"
        "Show all bugs"
        "List 10 stories related to cargo"
    """
    generic_types = {
        'all bugs': 'bugs',
        'show me all bugs': 'bugs',
        'list bugs': 'bugs',
        'all stories': 'stories',
        'show me all stories': 'stories',
        'list stories': 'stories',
        'all tasks': 'tasks',
        'show me all tasks': 'tasks',
        'list tasks': 'tasks',
        'all epics': 'epics',
        'show me all epics': 'epics',
        'list epics': 'epics',
        '': None
    }
    q = query.strip().lower()
    import json
    if q in generic_types:
        issue_type = generic_types[q]
        if not os.path.exists(JIRA_DATA_PATH):
            return [{"error": f"Jira data not found at {JIRA_DATA_PATH}"}]
        with open(JIRA_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if issue_type:
                issues = data.get(issue_type, [])
            else:
                issues = []
                for ktype in ['epics', 'stories', 'bugs', 'tasks']:
                    issues.extend(data.get(ktype, []))
            limited = issues[:k]
            response = []
            for issue in limited:
                response.append({
                    "text": jira_text_formatter(issue),
                    "metadata": issue
                })
            if len(limited) < k:
                response.append({
                    "info": f"Only {len(limited)} results found for your request."
                })
            return response
    # Otherwise, do a vector search
    results = jira_agent.query(query, top_k=k)
    if len(results) < k:
        results.append({"info": f"Only {len(results)} results found for your request."})
    return results