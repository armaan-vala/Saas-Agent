# 1️⃣ Imports
from src.sas_agent.utils.text_splitter import split_text
from src.sas_agent.vectorstore.chroma_service import add_document, retrieve_context, collection

# 2️⃣ Sample text to test chunking
text = "AI is transforming the world. It is used in healthcare, finance, and education."
print("Original Text:", text)

# 3️⃣ Split text into chunks
chunks = split_text(text, chunk_size=20, overlap=5)
print("\nChunks:")
for i, c in enumerate(chunks):
    print(f"Chunk {i}:", c)

# 4️⃣ Add chunks to ChromaDB under agent_id 'agent_test'
agent_id = "agent_test"
add_document(agent_id, chunks)
print(f"\n{len(chunks)} chunks added to Chroma for {agent_id}")

# 5️⃣ Retrieve context from Chroma using a query
query = "Where is AI used?"
retrieved = retrieve_context(agent_id, query, k=3)
print("\nRetrieved Context Chunks:")
for i, c in enumerate(retrieved):
    print(f"{i}:", c)

# 6️⃣ Simple check
if retrieved:
    print("\n✅ RAG backend helpers working properly!")
else:
    print("\n❌ Retrieval failed, check Chroma setup.")
