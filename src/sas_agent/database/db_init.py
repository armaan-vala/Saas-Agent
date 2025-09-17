import sqlite3
from pathlib import Path

# Database path inside database folder
DB_PATH = Path(__file__).parent / "sas_agent.db"

def init_db():
    """Initialize SQLite database with all required tables""" # <-- Updated docstring
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Agents table (your original code, unchanged)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Chat history table (your original code, unchanged)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER,
            user_message TEXT,
            agent_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(agent_id) REFERENCES agents(id)
        )
    ''')
    
    # --- NEW TABLE FOR DOCUMENT TRACKING ---
    # This is the new section being added.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(agent_id) REFERENCES agents(id)
        )
    ''')
    # --- END OF NEW SECTION ---

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

# Run directly to initialize DB
if __name__ == "__main__":
    init_db()