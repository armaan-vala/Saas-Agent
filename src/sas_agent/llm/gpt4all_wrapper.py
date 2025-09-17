import os
from pathlib import Path
from gpt4all import GPT4All

# Base directory = current folder (sas_agent)
BASE_DIR = Path(__file__).resolve().parent.parent
print("DEBUG: BASE_DIR =", BASE_DIR)

# Model path (pointing to mistral gguf file)
MODEL_FILE = BASE_DIR / "models" / "phi-2.Q4_0.gguf"
print("DEBUG: MODEL_FILE =", MODEL_FILE)
print("DEBUG: MODEL exists =", MODEL_FILE.exists())

# Check if model exists
if not MODEL_FILE.exists():
    raise FileNotFoundError(
        f"GPT4All model not found at {MODEL_FILE}. "
        f"Please place the .gguf model file in the models folder."
    )

# Load model
model = GPT4All(str(MODEL_FILE))

def ask_agent(prompt: str) -> str:
    """Ask something to the local GPT4All model"""
    with model.chat_session():
        response = model.generate(prompt, max_tokens=200)
    return response
