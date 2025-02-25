import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.run import api  # FastAPI application
from backend.app import app as flask_app
from json import JSONEncoder
from datetime import timedelta

# Add the project root to sys.path to resolve imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Import authentication helpers
from backend.api.auth.auth import create_access_token, get_current_user, create_refresh_token

# Create a test client for FastAPI
client = TestClient(api)

# JSON Encoder for serialization
jsone = JSONEncoder()

# Generate test JWT tokens
test_token = create_access_token(data={"sub": "TestUser"})  # Valid token
test_token_expired = create_access_token(data={"sub": "TestUser"}, expires_delta=timedelta(minutes=0))  # Expired token
test_refresh_token = create_refresh_token(data={"sub": "TestUser"})  # Refresh token
test_refresh_token_expired = create_refresh_token(data={"sub": "TestUser"}, expires_delta=timedelta(minutes=0))  # Expired refresh token


#### **TEST CASES FOR `/api/dive/divein` ENDPOINT** #####

@pytest.mark.asyncio
async def test_dive_in_expected_use():
    """
    Test the expected successful scenario of calling /divein API.
    - Uses a valid API key and username.
    - Mocks `DiverScraper.run_script()` to avoid actual Selenium execution.
    - Ensures the API returns a 200 status code.
    - Checks that the scraper was invoked exactly once.
    """
    form_data = {
        "username": "TestUser",         # Valid test username
        "api_key": "IvVnMKVsBmPrS5g7"   # Valid test API key
    }

    # Patch DiverScraper to prevent real web scraping
    with patch("backend.api.diveScript.diveScript.DiverScraper.run_script") as mock_run_script:
        mock_run_script.return_value = [{"Référence": "TestOrder123", "Articles Spécifiques": []}]  # Fake response

        # Simulate the Flask app context for database access
        with flask_app.app_context():
            response = client.post(
                "/api/dive/divein",  # Endpoint being tested
                data=form_data,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Bearer {test_token}"  # Valid JWT token
                }
            )

    # Assertions
    assert response.status_code == 200  # Expecting success response
    mock_run_script.assert_called_once()  # Ensure scraper was triggered once


@pytest.mark.asyncio
async def test_dive_in_unauthorized_access():
    """
    Test unauthorized access to /divein API.
    - Missing or incorrect JWT token should return 401 Unauthorized.
    """
    form_data = {
        "username": "TestUser",
        "api_key": "WrongApiKey"
    }

    response = client.post(
        "/api/dive/divein",
        data=form_data,
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer InvalidToken"  # Invalid JWT token
        }
    )

    # Expecting 401 Unauthorized since credentials are invalid
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dive_in_empty_scraper_response():
    """
    Test /divein API when the scraper returns no data.
    - Ensures the API still responds with 200 but returns an empty list.
    """
    form_data = {
        "username": "TestUser",
        "api_key": "IvVnMKVsBmPrS5g7"
    }

    with patch("backend.api.diveScript.diveScript.DiverScraper.run_script") as mock_run_script:
        mock_run_script.return_value = []  # Scraper returns no data

        with flask_app.app_context():
            response = client.post(
                "/api/dive/divein",
                data=form_data,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Bearer {test_token}"
                }
            )

    assert response.status_code == 200
    assert response.json()["message"] == []  # Expect empty list


@pytest.mark.asyncio
async def test_dive_in_expired_token():
    """
    Test /divein API with an expired JWT token.
    - The API should return 401 Unauthorized.
    """
    form_data = {
        "username": "TestUser",
        "api_key": "IvVnMKVsBmPrS5g7"
    }

    response = client.post(
        "/api/dive/divein",
        data=form_data,
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {test_token_expired}"  # Expired token
        }
    )

    assert response.status_code == 401  # Expecting Unauthorized


@pytest.mark.asyncio
async def test_dive_in_missing_token():
    """
    Test /divein API with no Authorization token.
    - Should return 401 Unauthorized.
    """
    form_data = {
        "username": "TestUser",
        "api_key": "IvVnMKVsBmPrS5g7"
    }

    response = client.post(
        "/api/dive/divein",
        data=form_data,
        headers={  # No Authorization header
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    assert response.status_code == 401

