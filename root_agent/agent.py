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
from .sub_agents.multitool_agent.agent import get_multiple_tool_agent
from . import prompt

MODEL = "gemini-2.0-flash"

def get_root_agent(session: Session):
    """
    Root agent orchestrating all sub-agents for enterprise knowledge memory.
    Routes queries to the appropriate sub-agent based on query context.
    """
    # Validate and reset session.state['tool'] to only valid tool names
    valid_tools = {"github", "jira", "confluence", "servicenow"}
    selected_tools = [t.lower() for t in session.state.get("tool", []) if t.lower() in valid_tools]
    session.state["tool"] = selected_tools

    tools = []

    # Single tool → include only that agent
    if len(selected_tools) == 1:
        tool = selected_tools[0]
        if tool == "github":
            tools.append(AgentTool(agent=get_github_agent(session)))
        elif tool == "jira":
            tools.append(AgentTool(agent=get_jira_agent(session)))
        elif tool == "confluence":
            tools.append(AgentTool(agent=get_confluence_agent(session)))
        elif tool == "servicenow":
            tools.append(AgentTool(agent=get_servicenow_agent(session)))

    # Multiple tools → use Multi-Tool agent
    elif len(selected_tools) > 1:
        tools.append(AgentTool(agent=get_multiple_tool_agent(session)))

    # If empty → optionally include all agents for query-based routing
    else:
        tools = [
            AgentTool(agent=get_github_agent(session)),
            AgentTool(agent=get_jira_agent(session)),
            AgentTool(agent=get_confluence_agent(session)),
            AgentTool(agent=get_servicenow_agent(session)),
        ]

    return Agent(
        name="Navo",
        model=MODEL,
        description=(
            "Orchestrates sub-agents (GitHub, Jira, Confluence, ServiceNow) with smart routing. "
            "- Single tool in preferences → route to that agent. "
            "- Multiple tools → use Multi-Tool agent. "
            "- Empty or no tool → route based on query keywords. "
            "- General queries → provide explanations or fallback guidance."
        ),
        instruction=prompt.ROOT_AGENT_PROMPT,
        output_key="root_agent_output",
        tools=tools,
    )
root_agent = get_root_agent