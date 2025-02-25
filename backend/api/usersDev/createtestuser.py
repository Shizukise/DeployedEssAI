from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.core.database import User
from backend.app import app
from backend.app import db
from backend.core.database import API_key
import secrets
import string

"""
Endpoint to create users
**At the moment for test users for development
"""

def generate_key(length):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

create_user_endpoint = APIRouter(prefix="/api/users/development")

@create_user_endpoint.post("/create")
async def createTestser():
    with app.app_context():
        new_test_user = User(username="TestUser",password="development",user_role="admin",team="team")
        db.session.add(new_test_user)
        db.session.commit()
        new_API_key = generate_key(16)
        new_API_key_object = API_key(key=new_API_key,assigned_to=new_test_user.user_id)
        db.session.add(new_API_key_object)
        db.session.commit()
        return JSONResponse(content={"message": "User created successfully"}, status_code=200)