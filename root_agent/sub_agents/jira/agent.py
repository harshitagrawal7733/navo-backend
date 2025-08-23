from google.adk.agents import Agent
from . import prompt
from root_agent.tools.jira_tool import fetch_jira_issues
# , semantic_jira_search

MODEL = "gemini-2.5-pro"

def get_jira_agent(session):
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
