# tools/github_tool.py

import json
import os

GITHUB_DATA_PATH = r"C:\Users\HSH164\navo-backend\navo-projects\Team001\project001\github.json"
from .vector_db_agent import VectorDBAgent

def github_text_formatter(issue):
    return f"Title: {issue.get('title', '')}\nBody: {issue.get('body', '')}"


def make_github_agent(collection_name, persist_dir, json_list_key, text_formatter):
    return VectorDBAgent(
        json_path=GITHUB_DATA_PATH,
        collection_name=collection_name,
        persist_dir=persist_dir,
        json_list_key=json_list_key,
        text_formatter=text_formatter
    )

github_agent = make_github_agent(
    collection_name="github_issues",
    persist_dir="./chroma_github",
    json_list_key="issues",
    text_formatter=github_text_formatter
)

def fetch_github_issues(query: str):
    """
    Query GitHub issues stored in ChromaDB using vector search.
    Returns top 3 most relevant issues.
    """
    return github_agent.query(query, top_k=3)

def fetch_github_prs(query: str):
    """Mock tool to search GitHub PR JSON for matches"""
    print(f"🔍 fetch_github_prs called with query: '{query}'")
    
    if not os.path.exists(GITHUB_DATA_PATH):
        print(f"❌ GitHub mock data file not found at path: {GITHUB_DATA_PATH}")
        return {"status": "error", "message": "GitHub mock data file not found"}

    print(f"📂 Loading GitHub PR data from: {GITHUB_DATA_PATH}")
    with open(GITHUB_DATA_PATH, "r") as f:
        prs = json.load(f)
    
    print(f"📄 Total PRs loaded: {len(prs)}")
    results = []

def github_pr_text_formatter(pr):
    return f"Title: {pr.get('title', '')}\nDescription: {pr.get('description', '')}"

github_pr_agent = make_github_agent(
    collection_name="github_prs",
    persist_dir="./chroma_github_prs",
    json_list_key="prs",
    text_formatter=github_pr_text_formatter
)

def fetch_github_prs(query: str):
    """
    Query GitHub PRs stored in ChromaDB using vector search.
    Returns top 3 most relevant PRs.
    """
    return github_pr_agent.query(query, top_k=3)
