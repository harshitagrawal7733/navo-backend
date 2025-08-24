# tools/confluence_tool.py

import json
import os
import logging

def fetch_confluence_pages(query: str):
    print(f"🔍 fetch_confluence_pages called with query: '{query}'")
    """Mock tool: fetch Confluence pages from a local JSON file."""
    json_path = r"\msk-cargo-quest-navo\navo-backend\maersk-projects\Team001\project001\confluence.json"
    
    if not os.path.exists(json_path):
        logging.error("❌ Confluence JSON not found.")
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
