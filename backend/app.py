import os
import requests
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from backend.core.config import db_api_uri
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


build_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend/build')

# Flask app initialization
app = Flask(__name__, static_folder=build_path, template_folder=build_path)


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# CORS setup for Flask (allow cross-origin requests from the React dev server)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Flask app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = db_api_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "377ab2df3fa073d5c00c95ea5398188651996a9717b4fdf77cf61ab191b897db"

# Initialize extensions
db.init_app(app)

bcrypt = Bcrypt(app)

# Serve React app only for non-api paths
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    # Don't serve React app for API paths
    if path.startswith("api"):
        return "API request is being handled by FastAPI.", 404  # Optionally return a 404 or 405 to prevent interference

    # In production, serve the React build files
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)

    # Default to serving index.html (React app's entry point)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/test')
def test_route():
	return "Flask is running!"
