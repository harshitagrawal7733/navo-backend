# tools/confluence_tool.py

import os
from .vector_db_agent import VectorDBAgent

# Use absolute path to ensure correct file loading
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CONFLUENCE_DATA_PATH = os.path.join(BASE_DIR, "data", "confluence", "projectA-docs.json")

# Debug: Print the path being used
print(f"Confluence tool loading data from: {CONFLUENCE_DATA_PATH}")
print(f"File exists: {os.path.exists(CONFLUENCE_DATA_PATH)}")

def confluence_text_formatter(page):
    return f"Title: {page.get('title', '')}\nContent: {page.get('content', '')}"

confluence_agent = VectorDBAgent(
    json_path=CONFLUENCE_DATA_PATH,
    collection_name="confluence_pages",
    persist_dir="chroma_store/chroma_confluence",
    json_list_key="pages",
    text_formatter=confluence_text_formatter
)

def fetch_confluence_pages(query: str):
    """
    Query Confluence pages stored in ChromaDB using vector search.
    Returns top 3 most relevant pages.
    """
    return confluence_agent.query(query, top_k=3)
