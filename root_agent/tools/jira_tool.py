import os
from .vector_db_agent import VectorDBAgent

# Use absolute path to ensure correct file loading
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
JIRA_DATA_PATH = os.path.join(BASE_DIR, "data", "jira", "issues.json")

# Debug: Print the path being used
print(f"Jira tool loading data from: {JIRA_DATA_PATH}")
print(f"File exists: {os.path.exists(JIRA_DATA_PATH)}")

def jira_text_formatter(issue):
    # Try to use id or key, and title or summary, for all types
    key = issue.get('id', issue.get('key', ''))
    title = issue.get('title', issue.get('summary', ''))
    desc = issue.get('description', '')
    status = issue.get('status', '')
    assignee = issue.get('assignee', '')
    return f"Key: {key}\nTitle: {title}\nStatus: {status}\nAssignee: {assignee}\nDescription: {desc}"

# Helper to flatten all issues for vector DB
def get_all_issues():
    import json
    if not os.path.exists(JIRA_DATA_PATH):
        return []
    with open(JIRA_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_issues = []
        for k in ['epics', 'stories', 'bugs', 'tasks']:
            all_issues.extend(data.get(k, []))
        return all_issues

# Write a temp file with all issues for vector DB
ALL_ISSUES_PATH = os.path.join(os.path.dirname(JIRA_DATA_PATH), 'all_issues.json')
if not os.path.exists(ALL_ISSUES_PATH):
    import json
    with open(ALL_ISSUES_PATH, 'w', encoding='utf-8') as f:
        json.dump(get_all_issues(), f, ensure_ascii=False, indent=2)

jira_agent = VectorDBAgent(
    json_path=ALL_ISSUES_PATH,
    collection_name="jira_issues",
    persist_dir="chroma_store/chroma_jira",
    json_list_key=None,
    text_formatter=jira_text_formatter
)

def fetch_jira_issues(query: str):
    """
    Query Jira issues stored in ChromaDB using vector search.
    For generic queries (e.g., 'all bugs', 'all stories', 'all tasks', 'all epics', or empty), return all of that type from JSON.
    Returns top 3 most relevant issues otherwise.
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
                # Return all issues if query is empty
                issues = []
                for k in ['epics', 'stories', 'bugs', 'tasks']:
                    issues.extend(data.get(k, []))
            return [
                {"text": jira_text_formatter(issue), "metadata": issue}
                for issue in issues
            ]
    # Otherwise, do a vector search
    return jira_agent.query(query, top_k=3)