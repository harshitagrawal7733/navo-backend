# tools/github_tool.py

import os
import json
from .vector_db_agent import VectorDBAgent
import logging
from root_agent.utils.preferences import PreferencesUtil

# Absolute path to ensure correct file loading
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
GITHUB_DATA_PATH = os.path.join(BASE_DIR, "data", "github", "github.json")

# Debug: Print the path being used
print(f"GitHub tool loading data from: {GITHUB_DATA_PATH}")
print(f"File exists: {os.path.exists(GITHUB_DATA_PATH)}")


def flatten_and_write(key, flat_path):
    if not os.path.exists(GITHUB_DATA_PATH):
        return
    with open(GITHUB_DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get(key, [])
        else:
            items = []
    with open(flat_path, 'w', encoding='utf-8') as f:
        json.dump({key: items}, f, indent=2)


PRS_FLAT_PATH = os.path.join(BASE_DIR, "data", "github", "prs_flat.json")
DISCUSSIONS_FLAT_PATH = os.path.join(BASE_DIR, "data", "github", "discussions_flat.json")
FILES_FLAT_PATH = os.path.join(BASE_DIR, "data", "github", "files_flat.json")

flatten_and_write("prs", PRS_FLAT_PATH)
flatten_and_write("discussions", DISCUSSIONS_FLAT_PATH)
flatten_and_write("files", FILES_FLAT_PATH)


def make_github_agent(collection_name, persist_dir, json_list_key, text_formatter, json_path):
    return VectorDBAgent(
        json_path=json_path,
        collection_name=collection_name,
        persist_dir=persist_dir,
        json_list_key=json_list_key,
        text_formatter=text_formatter
    )


# -----------------------
# GitHub PRs
# -----------------------
def github_pr_text_formatter(pr):
    # More detailed formatting
    details = [
        f"Title: {pr.get('title', '')}",
        f"Description: {pr.get('description', '')}",
        f"Status: {pr.get('status', '')}",
        f"Author: {pr.get('created_by', {}).get('name', '')}",
        f"Created At: {pr.get('created_at', '')}",
        f"URL: {pr.get('url', '')}"
    ]
    return "\n".join(details)


def github_pr_metadata(pr):
    # Keep metadata minimal to avoid large chunks
    return {
        "id": pr.get("id"),
        "title": pr.get("title"),
        "status": pr.get("status"),
        "author": pr.get("created_by", {}).get("name"),
        "created_at": pr.get("created_at"),
        "url": pr.get("url"),
    }


github_pr_agent = make_github_agent(
    collection_name="github_prs",
    persist_dir="chroma_store/chroma_github_prs",
    json_list_key="prs",
    text_formatter=github_pr_text_formatter,
    json_path=PRS_FLAT_PATH
)


def fetch_github_prs(query: str, k: int = 3):
    """
    User Intent:
    - Return up to 'k' GitHub PRs based on user query.
    - If fewer than 'k' results are found, inform the user how many were found.
    - Provide detailed PR info: title, description, status, author, created_at, url.
    - If no results, apologize and suggest follow-up queries.

    Example:
        "Bring me any 5 PRs from GitHub"
        "Show all open PRs"
    """
    generic_phrases = [
        '', 'all prs', 'show me all prs', 'show me prs',
        'list prs', 'list all prs', 'pull requests',
        'show pull requests', 'all pull requests', 'list pull requests',
    ]
    if query.strip().lower() in generic_phrases:
        if not os.path.exists(GITHUB_DATA_PATH):
            return [{"error": f"GitHub PR data not found at {GITHUB_DATA_PATH}"}]
        with open(GITHUB_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            prs = data.get('prs', [])
            limited = prs[:k]
            response = [
                {"text": github_pr_text_formatter(pr), "metadata": github_pr_metadata(pr)}
                for pr in limited
            ]
            if len(limited) < k:
                response.append({"info": f"Only {len(limited)} PRs found for your request."})
            return response
    results = github_pr_agent.query(query, top_k=k)
    if len(results) < k:
        results.append({"info": f"Only {len(results)} PRs found for your request."})
    return results


# -----------------------
# GitHub Discussions
# -----------------------
def github_discussion_text_formatter(disc):
    details = [
        f"Title: {disc.get('title', '')}",
        f"Details: {disc.get('details', '')}",
        f"Creator: {disc.get('created_by', {}).get('name', '')}",
        f"Created At: {disc.get('created_at', '')}",
        f"Status: {disc.get('status', '')}"
    ]
    return "\n".join(details)


def github_discussion_metadata(disc):
    return {
        "id": disc.get("id"),
        "title": disc.get("title"),
        "creator": disc.get("created_by", {}).get("name"),
        "created_at": disc.get("created_at"),
        "status": disc.get("status"),
    }


github_discussion_agent = make_github_agent(
    collection_name="github_discussions",
    persist_dir="chroma_store/chroma_github_discussions",
    json_list_key="discussions",
    text_formatter=github_discussion_text_formatter,
    json_path=DISCUSSIONS_FLAT_PATH
)


def fetch_github_discussions(query: str, k: int = 3):
    """
    User Intent:
    - Return up to 'k' GitHub discussions based on user query.
    - If fewer than 'k' results are found, inform the user how many were found.
    - Provide detailed discussion info: title, details, creator, created_at, status.
    - If no results, apologize and suggest follow-up queries.

    Example:
        "Show me 5 discussions about cargo"
    """
    generic_phrases = [
        '', 'all discussions', 'show me all discussions', 'show me discussions',
        'list discussions', 'list all discussions', 'github discussions',
        'show github discussions', 'all github discussions', 'list github discussions',
    ]
    if query.strip().lower() in generic_phrases:
        if not os.path.exists(GITHUB_DATA_PATH):
            return [{"error": f"GitHub discussion data not found at {GITHUB_DATA_PATH}"}]
        with open(GITHUB_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            discussions = data.get('discussions', [])
            limited = discussions[:k]
            response = [
                {"text": github_discussion_text_formatter(disc), "metadata": github_discussion_metadata(disc)}
                for disc in limited
            ]
            if len(limited) < k:
                response.append({"info": f"Only {len(limited)} discussions found for your request."})
            return response
    results = github_discussion_agent.query(query, top_k=k)
    if len(results) < k:
        results.append({"info": f"Only {len(results)} discussions found for your request."})
    return results


# -----------------------
# GitHub Files
# -----------------------
def github_file_text_formatter(file):
    content = file.get('content', '')
    if isinstance(content, str):
        lines = content.splitlines()
        preview = '\n'.join(lines[:10]) + '\n...' if len(lines) > 10 else content[:500]
    else:
        preview = str(content)[:500]
    details = [
        f"Path: {file.get('path', '')}",
        f"Repository: {file.get('repository', '')}",
        f"Type: {file.get('type', '')}",
        "Preview:",
        preview
    ]
    return "\n".join(details)


def github_file_metadata(file):
    return {
        "path": file.get("path"),
        "repository": file.get("repository"),
        "type": file.get("type"),
    }


github_file_agent = make_github_agent(
    collection_name="github_files",
    persist_dir="chroma_store/chroma_github_files",
    json_list_key="files",
    text_formatter=github_file_text_formatter,
    json_path=FILES_FLAT_PATH
)


def fetch_github_files(query: str, k: int = 3):
    """
    User Intent:
    - Return up to 'k' GitHub files based on user query.
    - If fewer than 'k' results are found, inform the user how many were found.
    - Provide detailed file info: path, preview, repository, type.
    - If no results, apologize and suggest follow-up queries.

    Example:
        "Show me 5 files related to booking"
    """
    results = github_file_agent.query(query, top_k=k)
    if len(results) < k:
        results.append({"info": f"Only {len(results)} files found for your request."})
    return results
