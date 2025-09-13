import sqlite3
from pathlib import Path

# Database path inside database folder
DB_PATH = Path(__file__).parent / "sas_agent.db"

def init_db():
    """Initialize SQLite database with agents and chat_history tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Agents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Chat history table
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

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

# Run directly to initialize DB
if __name__ == "__main__":
    init_db()
