from google.adk.agents import Agent
from . import prompt
from root_agent.tools.github_tool import fetch_github_prs

MODEL = "gemini-2.5-pro"

def get_github_agent(session):
    """
    User Intent:
    - Return up to 'k' results from GitHub (PRs, discussions, files) based on user query.
    - If fewer than 'k' results are found, inform the user how many were found.
    - Provide detailed information for each result, including title, description/details, author, status, and relevant metadata.
    - If no results are found, apologize and suggest possible follow-up queries.
    - Always try to understand the user's request for specific counts or types.

    Example:
        "Bring me any 5 results from GitHub"
        "Show all open PRs"
        "List 10 discussions about cargo"
    """
    instruction = f"""
{prompt.GITHUB_AGENT_PROMPT}

Your role:
- Perform tools search over GitHub PRs, commits, and discussions.
- Retrieve relevant historical context from the vector DB.
- Help generate summaries, draft PR descriptions, or answer context-aware engineering queries.
"""
    return Agent(
        model=MODEL,
        name="github_agent",
        description="Agent for semantic search in GitHub PRs/commits",
        output_key="github_agent_output",
        instruction=instruction,
        tools=[
            fetch_github_prs,
            # semantic_github_search,   # 🔹 custom retrieval tool
        ]
    )
