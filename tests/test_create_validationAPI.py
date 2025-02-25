import sys
import os

# Add the project root to sys.path to resolve imports like 'from execute.run import api'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, mock_open
from backend.run import api  # Importing the FastAPI application
from fastapi import UploadFile
from io import BytesIO
from backend.app import app as flask_app

# Create a TestClient instance for your FastAPI app
# This allows us to simulate HTTP requests without running the actual server
client = TestClient(api)

#Create function token imported from real endpoint, this is only to create a token that can be used trough testing
from backend.api.auth.auth import create_access_token,get_current_user

test_token = create_access_token(data={"sub": "TestUser"})

@pytest.mark.asyncio  # Indicates this test function is asynchronous
async def test_create_validation():
    """
    Test the endpoint with a single valid file.
    
    This test ensures:
    - The `/api/validation/create` endpoint can handle a single file upload.
    - The server responds with the correct status and message.
    - Filesystem-related operations (like checking if a directory exists) are correctly mocked.
    """
    # Mock the filesystem functions
    with patch("os.path.exists") as mock_exists, \
         patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", new_callable=MagicMock) as mock_open:  #A list containing the api key for the test user
        
        # Mock file input: Create a fake file-like object to simulate a PDF upload
        file_content = b"Fake PDF content"  # Binary content of the fake PDF file
        test_file = UploadFile(filename="test.pdf", file=BytesIO(file_content))
        files = [("files", ("test.pdf", test_file.file, "application/pdf"))]
        form_data = {
            "username" : "TestUser",
            "api_key" : "ifb183YcIvsRDMY3"  #This is the api_key for the testuser used for development
        }
        # Simulate the POST request to the API endpoint
        response = client.post(
            "/api/validation/create",
            files=files,  # Include the file in the request
            params=form_data,
            headers={"Authorization": f"Bearer {test_token}"}
        )
        print(response.json())
        # Assertions to check if the response is as expected
        assert response.status_code == 200  # Check if the HTTP status code is 200 (OK)
        assert response.json() == {"message": "Files uploaded successfully"}  # Check if the response contains the expected JSON message
        # Debugging: Print all calls made to os.path.exists for verification
        print(mock_exists.call_args_list)
        # Check that os.path.exists was called with the specific directory path
        mock_exists.assert_called_with("/home/galopin/project_root/backend/core/data/ToValidate")


@pytest.mark.asyncio  # Indicates this test function is asynchronous
async def test_create_validation_multiple():
    """ 
    Test the endpoint with multiple valid files.
    
    This test ensures:
    - The `/api/validation/create` endpoint can handle multiple file uploads.
    - The server responds with the correct status and message.
    - Filesystem-related operations (like checking if a directory exists) are correctly mocked.
    """
    # Mock the filesystem functions
    with patch("os.path.exists", return_value=False) as mock_exists, \
         patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", new_callable=MagicMock) as mock_open:

        # Mock file inputs: Create a list of fake file-like objects to simulate multiple PDF uploads
        file_contents = [b"Fake PDF content", b"Fake PDF content2", b"Fake PDF content3"]
        test_files = [
            ("files", (f"test_{i}.pdf", BytesIO(content), "application/pdf"))  # Format the files for the request
            for i, content in enumerate(file_contents)  # Enumerate through file contents to create unique file names
        ]

        form_data = {
            "username" : "TestUser",
            "api_key" : "ifb183YcIvsRDMY3"  #This is the api_key for the testuser used for development
        }

        # Simulate the POST request to the API endpoint
        response = client.post(
            "/api/validation/create",
            files=test_files,  # Include the list of files in the request
            params=form_data,
            headers={"Authorization": f"Bearer {test_token}"}
        )

        # Assertions to check if the response is as expected
        assert response.status_code == 200  # Check if the HTTP status code is 200 (OK)
        assert response.json() == {"message": "Files uploaded successfully"}  # Check if the response contains the expected JSON message

        # Debugging: Print all calls made to os.path.exists for verification
        print("Mock exists calls:", mock_exists.call_args_list)

        # Check that os.path.exists was called with the specific directory path
        mock_exists.assert_any_call("/home/galopin/project_root/backend/core/data/ToValidate")

        # Check that os.makedirs was called to create the directory
        mock_makedirs.assert_called_once_with("/home/galopin/project_root/backend/core/data/ToValidate")

@pytest.mark.asyncio
async def test_create_validation_nopdffile():
    """
    Test the endpoint with a single invalid file, other than PDF
    
    This test ensures:
    - The `/api/validation/create` endpoint rejects invalid file types.
    - The server responds with the correct status and message.
    """
    # Mock the filesystem functions
    with patch("os.path.exists") as mock_exists, \
         patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", new_callable=MagicMock) as mock_open:

        # Mock file input: Create a fake file-like object to simulate a JPG upload
        file_content = b"Fake JPG content"  # Binary content of the fake JPG file
        test_file = UploadFile(filename="test.jpg", file=BytesIO(file_content))
        
        form_data = {
            "username" : "TestUser",
            "api_key" : "ifb183YcIvsRDMY3"  #This is the api_key for the testuser used for development
        }

        # Simulate the POST request to the API endpoint
        response = client.post(
            "/api/validation/create",
            files={"files": ("test.jpg", test_file.file, "image/jpg")},  # Include the file in the request      
            params=form_data,
            headers={"Authorization": f"Bearer {test_token}"} 
        )

        # Assertions to check if the response is as expected
        assert response.status_code == 400  # Check if the HTTP status code is 400 (Bad Request)
        assert response.json() == {"message": "One or more files have unsupported types. Only PDF files are allowed."}  # Check if the response contains the expected JSON message

        # Ensure os.path.exists and os.makedirs are NOT called since validation failed early
        mock_exists.assert_not_called()
        mock_makedirs.assert_not_called()


@pytest.mark.asyncio
async def test_create_validation_badapple():
    """
    Test the endpoint with a single invalid file, other than PDF
    In the middle of valid PDF files.
    
    This test ensures:
    - The `/api/validation/create` endpoint rejects invalid file types.
    - The server responds with the correct status and message.
    """
    # Mock the filesystem functions
    with patch("os.path.exists") as mock_exists, \
         patch("os.makedirs") as mock_makedirs, \
         patch("builtins.open", new_callable=MagicMock) as mock_open:

        # Mock file input: Create a fake file-like object to simulate valid PDF uploads
        file_contents = [b"Fake PDF content", b"Fake PDF content2", b"Fake PDF content3"]
        test_files = [
            ("files", (f"test_{i}.pdf", BytesIO(content), "application/pdf"))  # Format the files for the request
            for i, content in enumerate(file_contents)  # Enumerate through file contents to create unique file names
        ]

        # Mock the invalid JPG file input
        bad_apple = b"Fake JPG content"
        test_bad_apple_file = UploadFile(filename="test.jpg", file=BytesIO(bad_apple))

        # Properly append the invalid JPG file in the same format
        test_files.append(("files", ("test.jpg", test_bad_apple_file.file, "image/jpg")))

        form_data = {
            "username" : "TestUser",
            "api_key" : "ifb183YcIvsRDMY3"  #This is the api_key for the testuser used for development
        }

        # Simulate the POST request to the API endpoint
        response = client.post(
            "/api/validation/create",
            files=test_files,
            params=form_data,
            headers={"Authorization": f"Bearer {test_token}"}
        )

        # Assertions to check if the response is as expected
        assert response.status_code == 400  # Check if the HTTP status code is 400 (Bad Request)
        assert response.json() == {"message": "One or more files have unsupported types. Only PDF files are allowed."}  # Check if the response contains the expected JSON message

        # Ensure os.path.exists and os.makedirs are NOT called since validation failed early
        mock_exists.assert_not_called()
        mock_makedirs.assert_not_called()


@pytest.mark.asyncio
async def test_create_validation_unauth_key():
    """
    Test the `/api/validation/create` endpoint with an unauthorized API key.

    Purpose:
    - Ensure that the endpoint rejects unauthorized API keys.
    - Verify that the response status code is 401 Unauthorized.
    - Confirm that no files are saved when an unauthorized API key is used.

    Mocked Dependencies:
    - Flask app context: Simulates the application context.
    - Database query: Returns a predefined mock API key.
    - File system functions (`os.path.exists`, `os.makedirs`): Avoids actual file system interactions.
    - Built-in `open` function: Prevents real file creation or writing.

    Steps:
    1. Mock the database to return a single authorized API key.
    2. Mock file operations to simulate the environment.
    3. Send a POST request with:
       - A mock PDF file.
       - Parameters including a username and an unauthorized API key.
    4. Validate that the response status code is 401 and includes the correct error message.
    5. Ensure no files were saved by verifying that `open` was not called.

    Assertions:
    - Response status code is 401.
    - Response body contains {"detail": "Unauthorized access"}.
    - The `open` function is not called.
    """
    # Create a mock key instance
    mock_key_instance = dict()
    mock_key_instance["key"] = "ifb183YcIvsRDMY3"

    # Mock Flask app context and database queries
    with flask_app.app_context():
        with patch("backend.core.database.API_key.query.all", return_value=[mock_key_instance]), \
             patch("os.path.exists", return_value=True), \
             patch("os.makedirs", return_value=None), \
             patch("builtins.open", new_callable=mock_open) as mock_open_func:

            # Create mock PDF file
            file_content = b"Fake PDF content"
            test_file = UploadFile(filename="test.pdf", file=BytesIO(file_content))
            files = [("files", ("test.pdf", test_file.file, "application/pdf"))]

            form_data = {
                "username": "TestUser",
                "api_key": "UnauthorizedKey",  # Unauthorized key
            }

            # Call API
            response = client.post("/api/validation/create", files=files, params=form_data,headers={"Authorization": f"Bearer {test_token}"})

            # Assert HTTP 401 response
            assert response.status_code == 401, f"Unexpected status code: {response.status_code}"

            # Ensure no files were saved
            mock_open_func.assert_not_called()


#Unauthorized access testing
@pytest.mark.asyncio
async def test_create_validation_no_jwt():
    response = client.post("/api/validation/create", files=[], params={})
    assert response.status_code == 401  
    assert response.json() == {"detail": "Not authenticated"}

@pytest.mark.asyncio
async def test_create_validation_invalid_jwt():
    response = client.post(
        "/api/validation/create",
        files=[],
        headers={"Authorization": "Bearer InvalidToken"}
    )
    assert response.status_code == 401  
    assert response.json() == {"detail": "Could not validate credentials"}

