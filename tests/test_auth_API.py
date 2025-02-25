import sys
import os

# Add the project root to sys.path to resolve imports like 'from execute.run import api'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, mock_open
from backend.run import api  # Importing the FastAPI application
from backend.app import app as flask_app
from json import JSONEncoder
from datetime import timedelta

# Create a TestClient instance for your FastAPI app
# This allows us to simulate HTTP requests without running the actual server
client = TestClient(api)

# Instantiate a JSON encoder for possible future use in tests
jsone = JSONEncoder()

# Import helper functions from the real endpoint
# These will assist in creating tokens and retrieving the current user
from backend.api.auth.auth import create_access_token, get_current_user,create_refresh_token

# Generate a test JWT token for use in the tests
# This token is tied to the username "testusername"
test_token = create_access_token(data={"sub": "TestUser"})
test_token_expired = create_access_token(data={"sub": "TestUser"}, expires_delta=timedelta(minutes=0))
test_refresh_token = create_refresh_token(data={"sub": "TestUser"})
test_refresh_token_expired = create_refresh_token(data={"sub": "TestUser"}, expires_delta=timedelta(minutes=0))

# Test the login endpoint with valid credentials
@pytest.mark.asyncio
async def test_login_valid():
    """
    Test the login endpoint with valid credentials.
    Ensure the endpoint returns a 200 status code on success.
    """
    form_data = {
        "username": "TestUser",         # A valid test username
        "password": "development"      # A valid password (API key for testing)
    }

    # Simulate the Flask application context for database queries
    with flask_app.app_context():
        # Send a POST request to the login endpoint
        response = client.post(
            "/api/auth/login",          # The login API endpoint
            data=form_data,             # Form data containing username and password
            headers={
                "accept": "application/json",                # Expecting a JSON response
                "Content-Type": "application/x-www-form-urlencoded"  # Form data encoding
            }
        )
    
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

# Test the login endpoint with an invalid username
@pytest.mark.asyncio
async def test_login_invalidusername():
    """
    Test the login endpoint with an invalid username.
    Ensure the endpoint returns a 400 status code and an appropriate error message.
    """
    form_data = {
        "username": "TestUser2223",    # An invalid username not present in the database
        "password": "development"     # Valid password
    }

    with flask_app.app_context():
        response = client.post(
            "/api/auth/login", 
            data=form_data, 
            headers={
                "accept": "application/json", 
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
    
    # Assert that the response status code is 400 (Bad Request)
    assert response.status_code == 400
    
    # Assert that the error message matches the expected output
    assert response.json() == {"message": "User does not exist"}

# Test the login endpoint with an invalid password
@pytest.mark.asyncio
async def test_login_invalidpassword():
    """
    Test the login endpoint with an invalid password.
    Ensure the endpoint returns a 400 status code and an appropriate error message.
    """
    form_data = {
        "username": "TestUser",         # A valid username
        "password": "developmentddddd" # An invalid password
    }

    with flask_app.app_context():
        response = client.post(
            "/api/auth/login", 
            data=form_data, 
            headers={
                "accept": "application/json", 
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
    
    # Assert that the response status code is 400 (Bad Request)
    assert response.status_code == 400  
    
    # Assert that the error message matches the expected output
    assert response.json() == {"message": "Wrong password, please try again"}

# Test the getusercreds endpoint with valid credentials
@pytest.mark.asyncio
async def test_getusercreds():
    """
    Test the getusercreds endpoint with a valid username and JWT token.
    Ensure the endpoint returns a 200 status code on success.
    """
    user = "TestUser"  # Valid username for the test

    with flask_app.app_context():
        response = client.get(
            f"/api/auth/getusercreds?username={user}", 
            headers={"Authorization": f"Bearer {test_token}"}  # Valid JWT token
        )
    
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

# Test the getusercreds endpoint with an invalid username
@pytest.mark.asyncio
async def test_getusercreds_invalid_username():
    """
    Test the getusercreds endpoint with an invalid username.
    Ensure the endpoint returns a 400 status code and an appropriate error message.
    """
    user = "invalid"  # Invalid username not present in the database

    with flask_app.app_context():
        response = client.get(
            f"/api/auth/getusercreds?username={user}",
            headers={"Authorization": f"Bearer {test_token}"}  # Valid JWT token
        )
    
    # Assert that the response status code is 400 (Bad Request)
    assert response.status_code == 400

# Test the getusercreds endpoint with an invalid or expired JWT token
@pytest.mark.asyncio
async def test_getusercreds_invalid_JWToken():
    """
    Test the getusercreds endpoint with an invalid or expired JWT token.
    Ensure the endpoint returns a 401 status code (Unauthorized).
    """
    user = "TestUser"  # Valid username for the test

    with flask_app.app_context():
        response = client.get(
            f"/api/auth/getusercreds?username={user}",
            headers={"Authorization": "Bearer invalid"}  # Invalid JWT token
        )
    
    # Assert that the response status code is 401 (Unauthorized)
    assert response.status_code == 401

# Test the getusercreds endpoint without providing a JWT token
@pytest.mark.asyncio
async def test_getusercreds_missing_JWToken():
    """
    Test the getusercreds endpoint without providing a JWT token.
    Ensure the endpoint returns a 401 status code (Unauthorized).
    """
    user = "TestUser"  # Valid username for the test

    with flask_app.app_context():
        response = client.get(f"/api/auth/getusercreds?username={user}")
    
    # Assert that the response status code is 401 (Unauthorized)
    assert response.status_code == 401

# Test the getusercreds endpoint with an expired JWT token
@pytest.mark.asyncio
async def test_getusercreds_expired_token():
    """
    Test the getusercreds endpoint with an expired JWT token.
    Ensure the endpoint returns a 401 status code (Unauthorized).
    """
    user = "TestUser"  # Valid username for the test

    with flask_app.app_context():
        # Send a GET request with an expired JWT token
        response = client.get(
            f"api/auth/getusercreds?username={user}",
            headers={"Authorization": f"Bearer {test_token_expired}"}
        )
    
    # Assert that the response status code is 401 (Unauthorized)
    assert response.status_code == 401

# Test the validateSession endpoint with a valid refresh token
@pytest.mark.asyncio
async def test_validatesession():
    """
    Test the validateSession endpoint with a valid refresh token.
    Ensure the endpoint returns a 200 status code (OK) on success.
    """
    with flask_app.app_context():
        form_data = {'username': 'TestUser'}
        response = client.post(
            "/api/auth/validateSession",
            data=form_data,
            headers={"Authorization": f"Bearer {test_refresh_token}"}  # Valid refresh token
        )
    assert response.status_code == 200  # Check if the session is active


# Test the validateSession endpoint with an expired refresh token
@pytest.mark.asyncio
async def test_validatesession_expired():
    """
    Test the validateSession endpoint with an expired refresh token.
    Ensure the endpoint returns a 401 status code (Unauthorized).
    """
    with flask_app.app_context():
        form_data = {'username': 'TestUser'}
        response = client.post(
            "/api/auth/validateSession",
            data=form_data,
            headers={"Authorization": f"Bearer {test_refresh_token_expired}"}  # Expired refresh token
        )
    assert response.status_code == 401


# Test the validateSession endpoint with an invalid token
@pytest.mark.asyncio
async def test_validatesession_invalidtoken():
    """
    Test the validateSession endpoint with an invalid token.
    Ensure the endpoint returns a 401 status code (Unauthorized).
    """
    with flask_app.app_context():
        form_data = {'username': 'TestUser'}
        response = client.post(
            "/api/auth/validateSession",
            data=form_data,
            headers={"Authorization": "Bearer 124524232"}  # Invalid token
        )
    assert response.status_code == 401


# Test the validateSession endpoint with a missing Authorization header
@pytest.mark.asyncio
async def test_validatesession_missing_auth_header():
    """
    Test the validateSession endpoint without an Authorization header.
    Ensure the endpoint returns a 401 status code (Unauthorized).
    """
    with flask_app.app_context():
        form_data = {'username': 'TestUser'}
        response = client.post("/api/auth/validateSession", data=form_data)  # No Authorization header
    assert response.status_code == 401


# Test the validateSession endpoint with a malformed Authorization header
@pytest.mark.asyncio
async def test_validatesession_malformed_auth_header():
    """
    Test the validateSession endpoint with a malformed Authorization header.
    Ensure the endpoint returns a 401 status code (Unauthorized).
    """
    with flask_app.app_context():
        form_data = {'username': 'TestUser'}
        response = client.post(
            "/api/auth/validateSession",
            data=form_data,
            headers={"Authorization": "InvalidHeaderFormat"}  # Malformed header
        )
    assert response.status_code == 401


# Test the refreshjwtoken endpoint with a valid refresh token
@pytest.mark.asyncio
async def test_refreshjwtoken():
    """
    Test the refreshjwtoken endpoint with a valid refresh token.
    Ensure the endpoint returns a 200 status code (OK) and a new JWT token.
    """
    with flask_app.app_context():
        form_data = {'username': 'TestUser'}
        response = client.post(
            "/api/auth/refreshjwtoken",
            data=form_data,
            headers={"Authorization": f"Bearer {test_refresh_token}"}  # Valid refresh token
        )
    assert response.status_code == 200


# Test the refreshjwtoken endpoint with an expired refresh token
@pytest.mark.asyncio
async def test_refreshjwtoken_expiredrefreshtoken():
    """
    Test the refreshjwtoken endpoint with an expired refresh token.
    Ensure the endpoint returns a 401 status code (Unauthorized).
    """
    with flask_app.app_context():
        form_data = {'username': 'TestUser'}
        response = client.post(
            "/api/auth/refreshjwtoken",
            data=form_data,
            headers={"Authorization": f"Bearer {test_refresh_token_expired}"}  # Expired token
        )
    assert response.status_code == 401


# Test the refreshjwtoken endpoint with missing username in the form data
@pytest.mark.asyncio
async def test_refreshjwtoken_missing_username():
    """
    Test the refreshjwtoken endpoint without providing the username in the form data.
    Ensure the endpoint returns a 422 status code (Unprocessable Entity).
    """
    with flask_app.app_context():
        form_data = {}  # Missing username
        response = client.post(
            "/api/auth/refreshjwtoken",
            data=form_data,
            headers={"Authorization": f"Bearer {test_refresh_token}"}
        )
    assert response.status_code == 422


# Test the refreshjwtoken endpoint with invalid form data
@pytest.mark.asyncio
async def test_refreshjwtoken_invalid_form_data():
    """
    Test the refreshjwtoken endpoint by sending JSON data instead of form data.
    Ensure the endpoint returns a 422 status code (Unprocessable Entity).
    """
    with flask_app.app_context():
        json_data = {"username": "TestUser"}  # JSON instead of form-encoded data
        response = client.post(
            "/api/auth/refreshjwtoken",
            json=json_data,  # Use JSON instead of form data
            headers={"Authorization": f"Bearer {test_refresh_token}"}
        )
    assert response.status_code == 422


# Test the refreshjwtoken endpoint with a malformed Authorization header
@pytest.mark.asyncio
async def test_refreshjwtoken_malformed_auth_header():
    """
    Test the refreshjwtoken endpoint with a malformed Authorization header.
    Ensure the endpoint returns a 401 status code (Unauthorized).
    """
    with flask_app.app_context():
        form_data = {'username': 'TestUser'}
        response = client.post(
            "/api/auth/refreshjwtoken",
            data=form_data,
            headers={"Authorization": "InvalidHeaderFormat"}  # Malformed header
        )
    assert response.status_code == 401


# Test the refreshjwtoken endpoint with a mismatched username
@pytest.mark.asyncio
async def test_refreshjwtoken_mismatched_username():
    """
    Test the refreshjwtoken endpoint where the username in the form data 
    does not match the refresh token's username.
    Ensure the endpoint returns a 401 status code (Unauthorized).
    """
    with flask_app.app_context():
        form_data = {'username': 'DifferentUser'}  # Mismatched username
        response = client.post(
            "/api/auth/refreshjwtoken",
            data=form_data,
            headers={"Authorization": f"Bearer {test_refresh_token}"}
        )
    assert response.status_code == 401