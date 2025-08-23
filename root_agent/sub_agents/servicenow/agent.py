from google.adk.agents import Agent
from . import prompt
from root_agent.tools.servicenow_tool import fetch_servicenow_incidents
# , semantic_servicenow_search

MODEL = "gemini-2.5-pro"

def get_servicenow_agent(session):
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
