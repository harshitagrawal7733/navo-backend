"""Root agent for enterprise memory & search"""
import os
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.sessions import InMemorySessionService, Session
import vertexai
from vertexai import agent_engines

from .sub_agents.github.agent import get_github_agent
from .sub_agents.jira.agent import get_jira_agent
from .sub_agents.confluence.agent import get_confluence_agent
from .sub_agents.servicenow.agent import get_servicenow_agent
from . import prompt

MODEL = "gemini-2.0-flash"

def get_root_agent(session: Session):
    """
    Root agent orchestrating all sub-agents for enterprise knowledge memory.
    Routes queries to the appropriate sub-agent based on query context.
    """
    return Agent(
        name="enterprise_memory_root_agent",
        model=MODEL,
        description=(
            "Orchestrates all sub-agents (GitHub, Jira, Confluence, ServiceNow) "
            "to provide contextual memory and knowledge reuse for engineering teams. "
            "If query is related to GitHub PRs, route to GitHub agent. "
            "If query is related to Jira tickets, route to Jira agent. "
            "If query is related to Confluence docs, route to Confluence agent. "
            "If query is related to ServiceNow incidents, route to ServiceNow agent. "
            "If the query is general or broad, provide fallback suggestions or memory retrieval guidance."
        ),
        instruction=prompt.ROOT_AGENT_PROMPT,
        output_key="root_agent_output",
        tools=[
            AgentTool(agent=get_github_agent(session)),
            AgentTool(agent=get_jira_agent(session)),
            AgentTool(agent=get_confluence_agent(session)),
            AgentTool(agent=get_servicenow_agent(session)),
        ],
    )

# Required by Google ADK CLI
root_agent = get_root_agent
