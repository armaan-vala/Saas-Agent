import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

project_name = "sas_agent"

list_of_files = [
    # GitHub workflow
    ".github/workflows/.gitkeep",

    # Main Flask entrypoint
    f"src/{project_name}/app.py",

    # Backend core
    f"src/{project_name}/routes/__init__.py",
    f"src/{project_name}/services/__init__.py",
    f"src/{project_name}/models/__init__.py",
    f"src/{project_name}/agents/__init__.py",

    # Database
    f"src/{project_name}/database/db_init.py",

    # Vector DB (RAG add-on later)
    f"src/{project_name}/vectorstore/chroma_service.py",

    # GPT4All wrapper
    f"src/{project_name}/llm/gpt4all_wrapper.py",

    # Utils
    f"src/{project_name}/utils/text_splitter.py",

    # Config
    "config/config.yaml",
    "requirements.txt",
    "setup.py",

    # Research
    "research/experiments.ipynb",

    # Frontend (templates + static)
    "templates/index.html",
    "templates/create_agent.html",
    "templates/chat.html",
    "static/css/style.css",
    "static/js/app.js",

    # Tests & docs
    "tests/__init__.py",
    "docs/README.md"
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for the file: {filename}")

    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
            logging.info(f"Creating empty file: {filepath}")
    else:
        logging.info(f"{filename} already exists")
