# tools/github_tool.py

import os
from .vector_db_agent import VectorDBAgent

# Use absolute path to ensure correct file loading
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
GITHUB_DATA_PATH = os.path.join(BASE_DIR, "data", "github", "db-repo.json")

# Debug: Print the path being used
print(f"GitHub tool loading data from: {GITHUB_DATA_PATH}")
print(f"File exists: {os.path.exists(GITHUB_DATA_PATH)}")

def make_github_agent(collection_name, persist_dir, json_list_key, text_formatter):
    return VectorDBAgent(
        json_path=GITHUB_DATA_PATH,
        collection_name=collection_name,
        persist_dir=persist_dir,
        json_list_key=json_list_key,
        text_formatter=text_formatter
    )

def github_pr_text_formatter(pr):
    return f"Title: {pr.get('title', '')}\nDescription: {pr.get('description', '')}"

github_pr_agent = make_github_agent(
    collection_name="github_prs",
    persist_dir="chroma_store/chroma_github_prs",
    json_list_key="prs",
    text_formatter=github_pr_text_formatter
)

def fetch_github_prs(query: str):
    """
    Query GitHub PRs stored in ChromaDB using vector search.
    For generic queries (e.g., 'all PRs', 'show me PRs', or empty), return all PRs from JSON.
    Returns top 3 most relevant PRs otherwise.
    """
    generic_phrases = [
        '',
        'all prs',
        'show me all prs',
        'show me prs',
        'list prs',
        'list all prs',
        'pull requests',
        'show pull requests',
        'all pull requests',
        'list pull requests',
    ]
    if query.strip().lower() in generic_phrases:
        # Load all PRs from JSON directly
        import json
        if not os.path.exists(GITHUB_DATA_PATH):
            return [{"error": f"GitHub PR data not found at {GITHUB_DATA_PATH}"}]
        with open(GITHUB_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            prs = data.get('prs', [])
            # Format each PR using the text formatter
            return [
                {"text": github_pr_text_formatter(pr), "metadata": pr}
                for pr in prs
            ]
    # Otherwise, do a vector search
    return github_pr_agent.query(query, top_k=3)

def github_discussion_text_formatter(disc):
    return f"Title: {disc.get('title', '')}\nDetails: {disc.get('details', '')}"

github_discussion_agent = make_github_agent(
    collection_name="github_discussions",
    persist_dir="chroma_store/chroma_github_discussions",
    json_list_key="discussions",
    text_formatter=github_discussion_text_formatter
)

def fetch_github_discussions(query: str):
    """
    Query GitHub discussions stored in ChromaDB using vector search.
    For generic queries (e.g., 'all discussions', 'show me discussions', or empty), return all discussions from JSON.
    Returns top 3 most relevant discussions otherwise.
    """
    generic_phrases = [
        '',
        'all discussions',
        'show me all discussions',
        'show me discussions',
        'list discussions',
        'list all discussions',
        'github discussions',
        'show github discussions',
        'all github discussions',
        'list github discussions',
    ]
    if query.strip().lower() in generic_phrases:
        # Load all discussions from JSON directly
        import json
        if not os.path.exists(GITHUB_DATA_PATH):
            return [{"error": f"GitHub discussion data not found at {GITHUB_DATA_PATH}"}]
        with open(GITHUB_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            discussions = data.get('discussions', [])
            # Format each discussion using the text formatter
            return [
                {"text": github_discussion_text_formatter(disc), "metadata": disc}
                for disc in discussions
            ]
    # Otherwise, do a vector search
    return github_discussion_agent.query(query, top_k=3)

def github_file_text_formatter(file):
    """
    Format a GitHub file for embedding and walkthroughs.
    Returns a summary with file path and a code/content preview (first 10 lines or 500 chars).
    """
    content = file.get('content', '')
    # Show only a preview for large files
    if isinstance(content, str):
        lines = content.splitlines()
        if len(lines) > 10:
            preview = '\n'.join(lines[:10]) + '\n...'
        else:
            preview = content[:500]
    else:
        preview = str(content)[:500]
    return f"Path: {file.get('path', '')}\nPreview:\n{preview}"

github_file_agent = make_github_agent(
    collection_name="github_files",
    persist_dir="chroma_store/chroma_github_files",
    json_list_key="files",
    text_formatter=github_file_text_formatter
)

def fetch_github_files(query: str):
    """
    Query GitHub files stored in ChromaDB using vector search.
    Returns top 3 most relevant files or code snippets for walkthroughs or code Q&A.
    """
    return github_file_agent.query(query, top_k=3)