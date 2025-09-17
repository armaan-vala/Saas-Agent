import os
import sqlite3
from ..utils.text_splitter import split_text
from ..vectorstore.chroma_service import add_document, delete_document_chunks
from ..database.db_init import DB_PATH

UPLOAD_FOLDER = "uploaded_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_file(agent_id, file):
    """Save file, read content, split and store in Chroma"""
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # For now handle only txt files
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = split_text(text)
    # This line was correctly updated in the previous step to include the filename
    add_document(agent_id, chunks, file.filename)
    return len(chunks)


def delete_document(doc_id):
    """Deletes a document from the SQL database and its chunks from ChromaDB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # First, get the agent_id and filename before we delete the record
    cursor.execute("SELECT agent_id, filename FROM documents WHERE id = ?", (doc_id,))
    doc_to_delete = cursor.fetchone()
    
    if not doc_to_delete:
        raise FileNotFoundError("Document not found in database.")
    
    agent_id = doc_to_delete['agent_id']
    filename = doc_to_delete['filename']
    
    # Delete from the SQL 'documents' table
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    
    # Delete the content from the ChromaDB vector store
    delete_document_chunks(str(agent_id), filename)
    
    return True