from google.adk.agents import Agent
from . import prompt
from root_agent.tools.jira_tool import fetch_jira_issues
# , semantic_jira_search

MODEL = "gemini-2.5-pro"

def get_jira_agent(query: str, k: int = 3):
    """
    User Intent:
    - Return up to 'k' Jira issues based on user query.
    - If fewer than 'k' results are found, inform the user how many were found.
    - Provide detailed information for each issue, including key, title, status, assignee, description, and relevant metadata.
    - If no results are found, apologize and suggest possible follow-up queries.
    - Always try to understand the user's request for specific counts or types.

    Example:
        "Bring me any 5 results from Jira"
        "Show all bugs"
        "List 10 stories related to cargo"
    """
    instruction = f"""
{prompt.JIRA_AGENT_PROMPT}

Your role:
- Perform semantic search over Jira tickets (past & active).
- Retrieve sprint history, bug reports, feature tickets.
- Help identify similar issues, blockers, or backlog trends.
"""
    return Agent(
        model=MODEL,
        name="jira_agent",
        description="Agent for semantic search in Jira tickets",
        output_key="jira_agent_output",
        instruction=instruction,
        tools=[
            fetch_jira_issues,
            # semantic_jira_search,   # 🔹 custom retrieval tool
        ]
    )
