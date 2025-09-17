import sqlite3
from flask import request, jsonify, render_template

# Your existing imports
from ..services.document_service import process_file
from ..services.chat_service import chat_with_agent
from ..llm.gpt4all_wrapper import ask_agent
from ..services.document_service import process_file, delete_document

def register_routes(app):

    # --- ROUTES TO SERVE THE HTML PAGES ---
    # These routes display the frontend to the user.

    @app.route("/")
    def index():
        """Serves the homepage (index.html)."""
        return render_template('index.html')

    @app.route("/create-agent")
    def create_agent_page():
        """Serves the create agent page (create_agent.html)."""
        return render_template('create_agent.html')

    @app.route("/chat")
    def chat_page():
        """Serves the chat interface page (chat.html)."""
        return render_template('chat.html')


    # --- EXISTING API ROUTES (Now prefixed with /api) ---
    # These routes are for the frontend JavaScript to send and receive data.

    @app.route("/api/chat", methods=["POST"])
    def chat():
        # This part remains the same
        data = request.get_json()
        agent_id = data.get("agent_id")
        query = data.get("query") or data.get("prompt")

        if not query:
            return jsonify({"error": "No query provided"}), 400

        # --- GENERATE THE RESPONSE ---
        try:
            if agent_id:
                answer = chat_with_agent(agent_id, query)
            else:
                answer = ask_agent(query)
        except Exception as e:
            print(f"Error during model generation: {e}")
            return jsonify({"error": "Failed to generate response from model."}), 500

        # --- NEW CODE BLOCK TO SAVE HISTORY ---
        # We save the conversation only if an agent_id is provided
        if agent_id:
            try:
                db_path = app.config['DATABASE_PATH']
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO chat_history (agent_id, user_message, agent_response) VALUES (?, ?, ?)',
                    (agent_id, query, answer)
                )
                conn.commit()
                conn.close()
                print(f"Saved chat history for agent_id: {agent_id}")
            except sqlite3.Error as e:
                # If saving fails, we still return the answer to the user.
                # We just print an error to the server log.
                print(f"Database error while saving chat history: {e}")
        # --- END OF NEW CODE BLOCK ---

        return jsonify({"response": answer})


    # In src/sas_agent/routes/__init__.py
    # Replace the old upload() function with this one.

    @app.route("/api/upload", methods=["POST"])
    def upload():
        agent_id = request.form.get("agent_id")
        file = request.files.get("file")

        if not agent_id or not file:
            return jsonify({"error": "agent_id or file missing"}), 400

        # --- PROCESS AND STORE IN VECTOR DB (No change here) ---
        try:
            chunks = process_file(agent_id, file)
            filename = file.filename
        except Exception as e:
            print(f"Error processing file for vector store: {e}")
            return jsonify({"error": "Failed to process the document."}), 500

        # --- NEW CODE BLOCK TO SAVE FILENAME RECORD ---
        try:
            db_path = app.config['DATABASE_PATH']
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO documents (agent_id, filename) VALUES (?, ?)',
                (agent_id, filename)
            )
            conn.commit()
            conn.close()
            print(f"Saved document record for agent_id {agent_id}: {filename}")
        except sqlite3.Error as e:
            # If saving the record fails, we don't want to fail the whole request
            # as the document is already in the vector store. We just log the error.
            print(f"Database error while saving document record: {e}")
        # --- END OF NEW CODE BLOCK ---

        return jsonify({"status": "success", "chunks_stored": chunks})


    # --- NEW AGENT MANAGEMENT API ROUTES ---
    # These are the new endpoints for creating and listing agents.

    @app.route("/api/agents", methods=['GET'])
    def get_agents():
        """
        API endpoint to retrieve a list of all agents from the database.
        """
        try:
            # Use the database path from the app's config
            db_path = app.config['DATABASE_PATH']
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, name, description FROM agents ORDER BY id DESC')
            agents_rows = cursor.fetchall()
            conn.close()

            agents_list = [dict(row) for row in agents_rows]
            return jsonify(agents_list), 200

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return jsonify({'error': 'An error occurred while fetching agents'}), 500

    @app.route("/api/create-agent", methods=['POST'])
    def create_agent_api():
        """
        API endpoint to create a new agent.
        Expects a JSON payload with 'name' and 'description'.
        """
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Agent name is required'}), 400

        name = data['name']
        description = data.get('description', '')

        try:
            db_path = app.config['DATABASE_PATH']
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO agents (name, description) VALUES (?, ?)',
                (name, description)
            )
            conn.commit()
            
            new_agent_id = cursor.lastrowid
            conn.close()

            return jsonify({
                'message': 'Agent created successfully',
                'agent_id': new_agent_id
            }), 201

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return jsonify({'error': 'An error occurred while creating the agent'}), 500
        

    @app.route("/api/agent/<int:agent_id>/history", methods=['GET'])
    def get_chat_history(agent_id):
        """
        API endpoint to retrieve the chat history for a specific agent.
        """
        try:
            db_path = app.config['DATABASE_PATH']
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Select all messages for the given agent_id, ordered by timestamp
            cursor.execute(
                'SELECT user_message, agent_response, timestamp FROM chat_history WHERE agent_id = ? ORDER BY timestamp ASC',
                (agent_id,)
            )
            history_rows = cursor.fetchall()
            conn.close()

            # Convert the database rows into a list of dictionaries
            history_list = [dict(row) for row in history_rows]
            
            return jsonify(history_list), 200

        except sqlite3.Error as e:
            print(f"Database error while fetching history: {e}")
            return jsonify({'error': 'An error occurred while fetching chat history'}), 500
        

    @app.route("/api/agent/<int:agent_id>/documents", methods=['GET'])
    def get_agent_documents(agent_id):
        """
        API endpoint to retrieve the list of documents for a specific agent.
        """
        try:
            db_path = app.config['DATABASE_PATH']
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Select all documents for the given agent_id, newest first
            cursor.execute(
                'SELECT id, filename, uploaded_at FROM documents WHERE agent_id = ? ORDER BY uploaded_at DESC',
                (agent_id,)
            )
            documents_rows = cursor.fetchall()
            conn.close()

            documents_list = [dict(row) for row in documents_rows]
            
            return jsonify(documents_list), 200

        except sqlite3.Error as e:
            print(f"Database error while fetching documents: {e}")
            return jsonify({'error': 'An error occurred while fetching documents'}), 500
        

    @app.route("/api/document/<int:doc_id>", methods=['DELETE'])
    def delete_document_route(doc_id):
        """API endpoint to delete a document."""
        try:
            delete_document(doc_id)
            return jsonify({"status": "success", "message": "Document deleted"}), 200
        except FileNotFoundError:
            return jsonify({"error": "Document not found"}), 404
        except Exception as e:
            print(f"Error deleting document: {e}")
            return jsonify({"error": "An internal error occurred"}), 500