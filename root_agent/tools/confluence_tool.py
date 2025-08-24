# tools/confluence_tool.py

from .vector_db_agent import VectorDBAgent

def confluence_text_formatter(page):
    return f"Title: {page.get('title', '')}\nContent: {page.get('content', '')}"

confluence_agent = VectorDBAgent(
    json_path=r"C:\Users\HSH164\navo-backend\navo-projects\Team001\project001\confluence.json",
    collection_name="confluence_pages",
    persist_dir="./chroma_confluence",
    json_list_key="pages",
    text_formatter=confluence_text_formatter
)

def fetch_confluence_pages(query: str):
    """
    Query Confluence pages stored in ChromaDB using vector search.
    Returns top 3 most relevant pages.
    """
    return confluence_agent.query(query, top_k=3)
