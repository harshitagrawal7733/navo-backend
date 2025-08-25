# tools/confluence_tool.py

import os
import json
from .vector_db_agent import VectorDBAgent
from root_agent.utils.preferences import PreferencesUtil

# Use absolute path to ensure correct file loading
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CONFLUENCE_DATA_PATH = os.path.join(BASE_DIR, "data", "confluence", "project001-docs.json")
FLATTENED_PATH = os.path.join(BASE_DIR, "data", "confluence", "project001-docs_flat.json")

# Debug: Print the path being used
print(f"Confluence tool loading data from: {CONFLUENCE_DATA_PATH}")
print(f"File exists: {os.path.exists(CONFLUENCE_DATA_PATH)}")

def flatten_pages(json_path):
    if not os.path.exists(json_path):
        return []
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get("pages", [])
        else:
            return []

flattened_pages = flatten_pages(CONFLUENCE_DATA_PATH)
with open(FLATTENED_PATH, "w", encoding="utf-8") as f:
    json.dump({"pages": flattened_pages}, f, indent=2)

def confluence_text_formatter(page):
    details = [
        f"Title: {page.get('title', '')}",
        f"Content: {page.get('content', '')}",
        f"Created By: {page.get('created_by', '')}",
        f"Created At: {page.get('created_at', '')}",
        f"Labels: {', '.join(page.get('labels', [])) if page.get('labels') else ''}"
    ]
    return "\n".join(details)

confluence_agent = VectorDBAgent(
    json_path=FLATTENED_PATH,
    collection_name="confluence_pages",
    persist_dir="chroma_store/chroma_confluence",
    json_list_key="pages",
    text_formatter=confluence_text_formatter
)

def fetch_confluence_pages(query: str, k: int = 3):
    """
    User Intent:
    - Return up to 'k' Confluence pages based on user query.
    - If fewer than 'k' results are found, inform the user how many were found.
    - Provide detailed page info: title, content, and any relevant metadata.
    - If no results, apologize and suggest follow-up queries.

    Example:
        "Show me 5 pages about system architecture"
    """
    results = confluence_agent.query(query, top_k=k)
    if len(results) < k:
        results.append({"info": f"Only {len(results)} pages found for your request."})
    return results