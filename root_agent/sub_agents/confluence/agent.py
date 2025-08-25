from google.adk.agents import Agent
from . import prompt
from root_agent.tools.confluence_tool import fetch_confluence_pages
# semantic_confluence_search

MODEL = "gemini-2.5-pro"

def get_confluence_agent(query: str, k: int = 3):
    """
    User Intent:
    - Return up to 'k' Confluence pages based on user query.
    - If fewer than 'k' results are found, inform the user how many were found.
    - Provide detailed information for each page, including title, content, and relevant metadata.
    - If no results are found, apologize and suggest possible follow-up queries.
    - Always try to understand the user's request for specific counts or topics.

    Example:
        "Show me 5 pages about system architecture"
        "List 10 pages about booking"
    """
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
