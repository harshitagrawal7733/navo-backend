from .vector_db_agent import VectorDBAgent

JIRA_DATA_PATH = r"C:\Users\HSH164\navo-backend\navo-projects\Team001\project001\jira.json"

def jira_text_formatter(issue):
    return f"Key: {issue.get('key', '')}\nSummary: {issue.get('summary', '')}\nDescription: {issue.get('description', '')}"

jira_agent = VectorDBAgent(
    json_path=r"C:\Users\HSH164\navo-backend\navo-projects\Team001\project001\jira.json",
    collection_name="jira_issues",
    persist_dir="./chroma_jira",
    json_list_key="issues",
    text_formatter=jira_text_formatter
)

def fetch_jira_issues(query: str):
    """
    Query Jira issues stored in ChromaDB using vector search.
    Returns top 3 most relevant issues.
    """
def fetch_jira_issues(query: str):
    return jira_agent.query(query, top_k=3)
