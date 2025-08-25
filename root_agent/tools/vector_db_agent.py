import os
import json
import chromadb
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SimpleNodeParser

class VectorDBAgent:
    MAX_METADATA_FIELD_LENGTH = 256  # Truncate metadata fields longer than this

    def __init__(
        self,
        json_path,
        collection_name,
        persist_dir,
        json_list_key,
        text_formatter,
        embed_model_name="sentence-transformers/all-MiniLM-L6-v2",
        chunk_size=2048,  # Increased chunk size to handle large metadata
    ):
        # Store initialization parameters
        self.json_path = json_path
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.json_list_key = json_list_key
        self.text_formatter = text_formatter
        self.chunk_size = chunk_size

        # Load the embedding model for semantic search
        self.embed_model = HuggingFaceEmbedding(model_name=embed_model_name)

        # Connect to (or create) the persistent Chroma vector database
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.chroma_collection = self.client.get_or_create_collection(self.collection_name)
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        # Node parser with larger chunk size
        self.node_parser = SimpleNodeParser(chunk_size=self.chunk_size, chunk_overlap=100)

        # If the collection is empty, load and index data from JSON
        if self.chroma_collection.count() == 0:
            documents = self.load_data()
            # Build a new vector index from the loaded documents
            self.index = VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context,
                embed_model=self.embed_model,
                node_parser=self.node_parser
            )
        else:
            # Otherwise, just load the existing index from the vector store
            self.index = VectorStoreIndex.from_vector_store(
                self.vector_store, embed_model=self.embed_model
            )

    def load_data(self):
        # Load and parse the JSON data file
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"JSON not found: {self.json_path}")

        with open(self.json_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        # Determine which part of JSON to use
        if self.json_list_key is None:
            if isinstance(loaded, list):
                data = loaded
            elif isinstance(loaded, dict):
                data = []
                for v in loaded.values():
                    if isinstance(v, list):
                        data.extend(v)
            else:
                raise ValueError(f"Unexpected JSON structure in {self.json_path}: {type(loaded)}")
        elif isinstance(loaded, dict):
            data = loaded.get(self.json_list_key, [])
        elif isinstance(loaded, list):
            data = loaded
        else:
            raise ValueError(f"Unexpected JSON structure in {self.json_path}: {type(loaded)}")

        docs = []
        for item in data:
            # Format the text for embedding
            text = self.text_formatter(item)

            # Flatten metadata and truncate long fields
            flat_metadata = {}
            for k, v in item.items():
                if isinstance(v, (list, dict)):
                    json_str = json.dumps(v, ensure_ascii=False)
                    flat_metadata[k] = (
                        json_str[:self.MAX_METADATA_FIELD_LENGTH] + "..."
                        if len(json_str) > self.MAX_METADATA_FIELD_LENGTH
                        else json_str
                    )
                else:
                    str_v = str(v)
                    flat_metadata[k] = (
                        str_v[:self.MAX_METADATA_FIELD_LENGTH] + "..."
                        if len(str_v) > self.MAX_METADATA_FIELD_LENGTH
                        else str_v
                    )

            docs.append(Document(text=text, metadata=flat_metadata))

        return docs

    def query(self, query, top_k=3):
        if not query:
            return {"error": "Please provide a query."}

        retriever = self.index.as_retriever(similarity_top_k=top_k)
        results = retriever.retrieve(query)

        response = []
        for r in results:
            response.append({
                "text": r.node.text,
                "score": r.score,
                "metadata": r.node.metadata
            })
        return response
