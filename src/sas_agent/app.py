from flask import Flask
# Import DB_PATH as well, so we can pass it to our routes
from .database.db_init import init_db, DB_PATH
from .routes import register_routes

# Correct the paths to your templates and static folders
app = Flask(__name__, template_folder='../../templates', static_folder='../../static')

# Add the database path to the app's configuration.
# This allows our routes in the other file to access the path reliably.
app.config['DATABASE_PATH'] = DB_PATH

# Initialize database
init_db()

# Register all routes from routes/__init__.py
register_routes(app)

if __name__ == "__main__":
    print(app.url_map)  # Debug: shows all registered routes
    app.run(debug=True)