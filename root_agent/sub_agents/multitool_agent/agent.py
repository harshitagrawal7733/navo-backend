from google.adk.agents import ParallelAgent
import logging

from . import prompt 
from ..github.agent import get_github_agent
from ..jira.agent import get_jira_agent
from ..confluence.agent import get_confluence_agent
from ..servicenow.agent import get_servicenow_agent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


class MultiToolAgent(ParallelAgent):
    """
    ParallelAgent subclass that can merge responses from multiple sub-agents.
    """
    def run_and_merge(self, query: str) -> str:
        """
        Run the query across all sub-agents and merge their responses.
        """
        responses = self.run(query)  # This returns dict: {agent_name: response}
        merged = []
        for agent_name, resp in responses.items():
            if resp:
                merged.append(f"### {agent_name.capitalize()} Response\n{resp}\n")
        if not merged:
            return "⚠️ No responses received from any agent."
        return "\n".join(merged)


def get_multiple_tool_agent(session):
    logger.info("Initializing enterprise agent with parallel sub-agents...")

    # Get tool preferences from session (case-insensitive mapping)
    requested_tools = [t.lower() for t in session.state.get("tool", [])]
    logger.info(f"🔄 session preferences for multitool: {session.state}")

    # Map all possible agents
    available_agents = {
        "github": get_github_agent(session),
        "jira": get_jira_agent(session),
        "confluence": get_confluence_agent(session),
        "servicenow": get_servicenow_agent(session),
    }

    # Filter agents based on requested tools
    sub_agents = []
    for name, agent_instance in available_agents.items():
        if name in requested_tools:
            try:
                sub_agents.append(agent_instance)
                logger.info(f"✅ Initialized {name} agent: {agent_instance.name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {name} agent: {e}")

    if not sub_agents:
        logger.warning("No requested enterprise sub-agents were successfully initialized.")
        class DummyAgent:
            name = "No Tool"
            def run(self, query):
                return ("Sorry, no valid tools were selected. "
                        "Please choose from: GitHub, Jira, Confluence, or ServiceNow.")
        return DummyAgent()

    enterprise_agent = MultiToolAgent(
        name="enterprise_queries_agent",
        description="Handles enterprise queries using parallel agents based on user preferences.",
        sub_agents=sub_agents
    )

    return enterprise_agent

