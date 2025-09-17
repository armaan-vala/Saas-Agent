import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

# Chroma client init
client = chromadb.PersistentClient(path=str(Path("sas_agent_chroma")))

# Default collection
collection = client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
)

def add_document(agent_id, chunks, filename): # Add filename here
    """Add document chunks for a specific agent into ChromaDB"""
    ids = [f"{agent_id}_{filename}_{i}" for i in range(len(chunks))] # Make IDs more unique
    # Add filename to the metadata
    metadatas=[{"agent": agent_id, "filename": filename}] * len(chunks)
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)

def retrieve_context(agent_id, query, k=3):
    """Retrieve top-k chunks for an agent based on query"""
    results = collection.query(query_texts=[query], n_results=k, where={"agent": agent_id})
    return results.get("documents", [[]])[0]



def delete_document_chunks(agent_id, filename):
    """Delete all chunks associated with a specific file for an agent."""
    collection.delete(where={"agent": agent_id, "filename": filename})
    print(f"Deleted chunks from ChromaDB for agent {agent_id} and file {filename}")