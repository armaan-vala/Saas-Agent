from ..vectorstore.chroma_service import retrieve_context
from ..llm.gpt4all_wrapper import ask_agent as generate_response

def chat_with_agent(agent_id, query):
    """RAG-powered chat flow"""
    # Retrieve relevant context
    context_chunks = retrieve_context(agent_id, query)
    context_text = "\n".join(context_chunks)

    # Build prompt
    prompt = f"Use the following context to answer:\n{context_text}\n\nUser: {query}\nAnswer:"

    # Generate reply from GPT4All
    return generate_response(prompt)
