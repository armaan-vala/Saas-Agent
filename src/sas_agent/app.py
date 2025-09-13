from flask import Flask, request, jsonify
from database.db_init import init_db
from llm.gpt4all_wrapper import ask_agent

app = Flask(__name__)

# Initialize database
init_db()


# Simple Hello World route
@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello World! SAS Agent backend running ✅"})


# homepage index page
@app.route("/", methods=["GET"])
def home():
    return "<h2>SAS Agent Backend Running ✅ Go to /hello or use POST /chat</h2>"


# Basic chat route (GPT4All)
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt", "")
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    response = ask_agent(prompt)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
