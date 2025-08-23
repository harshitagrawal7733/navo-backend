# tools/confluence_tool.py

import json
import os

def fetch_confluence_pages(query: str):
    """Mock tool: fetch Confluence pages from a local JSON file."""
    json_path = r"C:\Users\HAG047\OneDrive - Maersk Group\Documents\msk-cargo-quest-navo\navo-backend\maersk-projects\Team001\project001\confluence.json"
    
    if not os.path.exists(json_path):
        return {"error": "Confluence JSON not found."}

    with open(json_path, "r", encoding="utf-8") as f:
        pages = json.load(f).get("pages", [])

    # If a query is provided, do simple filter
    if query:
        filtered = [p for p in pages if query.lower() in (p.get("title", "") + p.get("content", "")).lower()]
    else:
        filtered = pages

    # Return top 3 results
    return filtered[:3]
