import os
import json
import chromadb
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

class VectorDBAgent:
    def __init__(
        self,
        json_path,
        collection_name,
        persist_dir,
        json_list_key,
        text_formatter,
        embed_model_name="sentence-transformers/all-MiniLM-L6-v2",
    ):
        # Store initialization parameters
        self.json_path = json_path
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.json_list_key = json_list_key
        self.text_formatter = text_formatter
        # Load the embedding model for semantic search
        self.embed_model = HuggingFaceEmbedding(model_name=embed_model_name)

        # Connect to (or create) the persistent Chroma vector database
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.chroma_collection = self.client.get_or_create_collection(self.collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        # If the collection is empty, load and index data from JSON
        if self.chroma_collection.count() == 0:
            documents = self.load_data()
            # Build a new vector index from the loaded documents
            self.index = VectorStoreIndex.from_documents(
                documents, storage_context=self.storage_context, embed_model=self.embed_model
            )
        else:
            # Otherwise, just load the existing index from the vector store
            self.index = VectorStoreIndex.from_vector_store(self.vector_store, embed_model=self.embed_model)

    def load_data(self):
        # Load and parse the JSON data file
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"JSON not found: {self.json_path}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            # Support both dict and list top-level JSON structures
            if isinstance(loaded, dict):
                data = loaded.get(self.json_list_key, [])
            elif isinstance(loaded, list):
                data = loaded
            else:
                raise ValueError(f"Unexpected JSON structure in {self.json_path}: {type(loaded)}")
        docs = []
        for item in data:
            # Format the text for embedding
            text = self.text_formatter(item)
            # Flatten metadata: convert lists/dicts to JSON strings for compatibility with vector DB
            flat_metadata = {}
            for k, v in item.items():
                if isinstance(v, (list, dict)):
                    flat_metadata[k] = json.dumps(v, ensure_ascii=False)
                else:
                    flat_metadata[k] = v
            # Create a Document with the formatted text and flattened metadata
            docs.append(Document(text=text, metadata=flat_metadata))
        return docs

    def query(self, query, top_k=3):
        # Return error if query is empty
        if not query:
            return {"error": "Please provide a query."}
        # Use the vector index to retrieve the most similar documents
        retriever = self.index.as_retriever(similarity_top_k=top_k)
        results = retriever.retrieve(query)
        response = []
        for r in results:
            response.append({
                "text": r.node.text,      # The main text content
                "score": r.score,         # Similarity score
                "metadata": r.node.metadata  # Associated metadata
            })
        return response
