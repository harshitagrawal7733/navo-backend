# Format a ServiceNow incident for embedding
import os
from .vector_db_agent import VectorDBAgent

# Use absolute path to ensure correct file loading
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SERVICENOW_DATA_PATH = os.path.join(BASE_DIR, "data", "servicenow", "incidents.json")

# Debug: Print the path being used
print(f"ServiceNow tool loading data from: {SERVICENOW_DATA_PATH}")
print(f"File exists: {os.path.exists(SERVICENOW_DATA_PATH)}")

def servicenow_text_formatter(inc):
    """
    Format a ServiceNow incident dictionary into a string for embedding.
    """
    return f"Title: {inc.get('title', '')}\nDescription: {inc.get('description', '')}"

# Create a vector database agent for ServiceNow incidents
servicenow_agent = VectorDBAgent(
    json_path=SERVICENOW_DATA_PATH,
    collection_name="servicenow_incidents",
    persist_dir="chroma_store/chroma_servicenow",
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
