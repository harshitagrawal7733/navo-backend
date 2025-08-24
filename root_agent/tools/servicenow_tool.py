# Format a ServiceNow incident for embedding
from .vector_db_agent import VectorDBAgent

def servicenow_text_formatter(inc):
    """
    Format a ServiceNow incident dictionary into a string for embedding.
    """
    return f"Title: {inc.get('title', '')}\nDescription: {inc.get('description', '')}"

# Create a vector database agent for ServiceNow incidents
servicenow_agent = VectorDBAgent(
    json_path=r"C:\Users\HSH164\navo-backend\navo-projects\Team001\project001\servicenow..json",
    collection_name="servicenow_incidents",
    persist_dir="./chroma_servicenow",
    json_list_key="incidents",
    text_formatter=servicenow_text_formatter
)

# Query ServiceNow incidents using semantic search
def fetch_servicenow_incidents(query: str):
    """
    Query ServiceNow incidents stored in ChromaDB using vector search.
    Returns top 3 most relevant incidents.
    """
    return servicenow_agent.query(query, top_k=3)
