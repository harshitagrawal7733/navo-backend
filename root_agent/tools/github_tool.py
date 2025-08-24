# tools/github_tool.py

import json
import os

GITHUB_DATA_PATH = r"C:\Users\HAG047\OneDrive - Maersk Group\Documents\msk-cargo-quest-navo\navo-backend\maersk-projects\Team001\project001\github.json"

def fetch_github_prs(query: str):
    print(f"🔍 fetch_github_prs called with query: '{query}'")
    """Mock tool to search GitHub PR JSON for matches"""
    
    if not os.path.exists(GITHUB_DATA_PATH):
        print(f"❌ GitHub mock data file not found at path: {GITHUB_DATA_PATH}")
        return {"status": "error", "message": "GitHub mock data file not found"}

    print(f"📂 Loading GitHub PR data from: {GITHUB_DATA_PATH}")
    with open(GITHUB_DATA_PATH, "r") as f:
        prs = json.load(f)
    
    print(f"📄 Total PRs loaded: {len(prs)}")
    results = []

    for pr in prs:
        text = (pr.get("title", "") + " " + pr.get("description", "")).lower()
        if query.lower() in text:
            results.append(pr)
    
    print(f"✅ Found {len(results)} matching PR(s) for query: '{query}'")
    top_results = results[:3]
    for idx, pr in enumerate(top_results, start=1):
        print(f"  {idx}. PR #{pr.get('id', 'N/A')} - {pr.get('title', 'No Title')} by {pr.get('author', 'Unknown')}")
    
    return {
        "status": "success",
        "results": top_results  # return top 3 matches
    }
