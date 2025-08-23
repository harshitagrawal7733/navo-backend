from google.adk.agents import Agent
from . import prompt
from root_agent.tools.confluence_tool import fetch_confluence_pages
# semantic_confluence_search

MODEL = "gemini-2.5-pro"

def get_confluence_agent(session):
    instruction = f"""
{prompt.CONFLUENCE_AGENT_PROMPT}

Your role:
- Perform semantic search over Confluence pages and spaces.
- Retrieve docs like onboarding guides, design docs, retrospectives.
- Provide summaries or answer context-aware queries using stored embeddings.
"""
    return Agent(
        model=MODEL,
        name="confluence_agent",
        description="Agent for semantic search in Confluence docs",
        output_key="confluence_agent_output",
        instruction=instruction,
        tools=[
            fetch_confluence_pages,
            # semantic_confluence_search,  # 🔹 custom retrieval tool
        ]
    )
