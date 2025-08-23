from google.adk.agents import Agent
from . import prompt
from root_agent.tools.github_tool import fetch_github_prs

MODEL = "gemini-2.5-pro"

def get_github_agent(session):
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
