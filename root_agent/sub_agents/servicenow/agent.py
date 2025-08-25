from google.adk.agents import Agent
from . import prompt
from root_agent.tools.servicenow_tool import fetch_servicenow_incidents
# , semantic_servicenow_search

MODEL = "gemini-2.5-pro"

def get_servicenow_agent(query: str, k: int = 3):
    """
    User Intent:
    - Return up to 'k' ServiceNow incidents based on user query.
    - If fewer than 'k' results are found, inform the user how many were found.
    - Provide detailed information for each incident, including ID, title, description, status, root cause, resolution, steps, comments, and linked resources.
    - If no results are found, apologize and suggest possible follow-up queries.
    - Always try to understand the user's request for specific counts or incident numbers.

    Example:
        "Bring me any 5 incidents from ServiceNow"
        "Show all critical incidents"
        "List 10 incidents related to booking"
    """
    instruction = f"""
{prompt.SERVICENOW_AGENT_PROMPT}

Your role:
- Perform semantic search over ServiceNow incidents and change requests.
- Retrieve incident history, resolution steps, SLA violations.
- Provide context-aware insights for ITSM workflows.
"""
    return Agent(
        model=MODEL,
        name="servicenow_agent",
        description="Agent for semantic search in ServiceNow incidents",
        output_key="servicenow_agent_output",
        instruction=instruction,
        tools=[
            fetch_servicenow_incidents,
            # semantic_servicenow_search,   # 🔹 custom retrieval tool
        ]
    )
