import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from backend.app import app as flask_app  
from backend.api.tickets.crud import ticket_api, test_api_router
from backend.api.validations.crud import validation_api
from backend.core.database import *
from backend.api.tickets.models import *
from backend.api.validations.models import *
from backend.api.diveScript.models import *
from backend.api.usersDev.createtestuser import create_user_endpoint
from backend.api.auth.auth import authApi
from backend.api.diveScript.API import DiveAPI

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Create tables before running the FastAPI server
with flask_app.app_context():
    db.create_all()  # Ensure tables are created before serving

# Initialize FastAPI application
api = FastAPI()

# Add CORS middleware to allow cross-origin requests from React
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
		   "http://134.122.108.55:5000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow POST method here
    allow_headers=["*"],  # Allow all headers
)

# Mount FastAPI to handle /api/* routes
api.include_router(ticket_api)  # Include ticket-related routes
api.include_router(test_api_router)  # Include test API routes
api.include_router(validation_api)  #Include validation API routes
api.include_router(create_user_endpoint) # development endpoint to create test user
api.include_router(authApi)
api.include_router(DiveAPI)


# Mount Flask under the root path to serve React app for non-API routes
flask_asgi = WSGIMiddleware(flask_app)
api.mount("/", flask_asgi)  # Flask app for non-API routes

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)
