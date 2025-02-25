from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.app import app as flask_app, bcrypt
from backend.core.database import User, API_key

#FastAPI JWTtoken configurations
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt


#Access token (short lived)
SECRET_KEY = "377ab2df3fa073d5c00c95ea5398188651996a9717b4fdf77cf61ab191b897db"  #This should be on a config file later on
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

#refresh tokens configs
REFRESH_SECRET_KEY = "your_refresh_secret_key"  # Keep this separate from the access token key
REFRESH_ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_MINUTES = 420     ###SUPER IMPORTANT, NEED A MECHANISM TO DELETE TOKEN AFTER EXPIRED (REFRESH TOKEN ONLY) DONE? ValidateSession method

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

authApi = APIRouter(prefix="/api/auth")

# Standard function to create JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    This one might be called multiple times, as this is the one that 
    whill be called when refreshing a token using the refresh token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Default to 30 minutes
    to_encode = data.copy()
    try:
        expire = datetime.utcnow() + expires_delta
    except Exception as e:
        print(f"Error calculating expiration time: {e}")
        raise
    to_encode.update({"exp": expire})
    print(f"Expiration time: {expire}")
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Same for refresh_tokens
def create_refresh_token(data: dict, expires_delta: timedelta = None):
    """
    This function might be called only once(not a requesite)
    But a refresh token lasts for a lot longer and there is no need
    to create another one except for logins or server side security problems.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    try:
        expire = datetime.utcnow() + expires_delta
    except Exception as e:
        print(f"Error calculating expiration time: {e}")
        raise
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=REFRESH_ALGORITHM)

""" # In context with above function, this endpoint will be called to refresh an user token using a refresh token (with a bigger expiration date)
@authApi.post("/refresh-token")
async def refresh_token(refresh_token: str = Form(...)):
    try:
        # Decode the refresh token
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[REFRESH_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Create a new access token
        new_access_token = create_access_token(data={"sub": username})
        return JSONResponse(content={"message": "User logged in", "access_token": new_access_token, "token_type" : "bearer"}, status_code=200)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token") ???????????????????????????????????????????????????????""" 

# Function to get current user from the JWT token
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username

# Function to get current user from the Refresh Token
def get_current_user2(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[REFRESH_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return username


# Define a Pydantic model for user-related data
class UserName(BaseModel):
    username: str = Form(...)  # Username field is required and must be provided in form data


# Endpoint for user login
@authApi.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Authenticates a user based on their username and password.
    Args:
        username (str): The username provided by the user.
        password (str): The password provided by the user.
    Returns:
        JSONResponse: A response indicating success or failure of the login attempt.
    """
    try:
        # Use Flask's app context to query the database
        with flask_app.app_context():
            user = User.query.filter_by(username=username).first()  # Find the user by username
            if not user:
                # Return a 404 error if the user does not exist
                return JSONResponse(content={"message": "User does not exist"}, status_code=400)
            if bcrypt.check_password_hash(user.password_hash, password):
                # If password matches, return the JWT toke
                access_token = create_access_token(data={"sub": username})
                refresh_token = create_refresh_token(data={"sub": username})
                
                return JSONResponse(content={"message": "User logged in", "access_token": access_token, "refresh_token" : refresh_token,
                                            "token_type" : "bearer"}, status_code=200)
            else:
                # If password does not match, return a 400 error
                return JSONResponse(content={"message": "Wrong password, please try again"}, status_code=400)
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(500, detail=f"An internal error occurred: {e}")


# Endpoint to retrieve user credentials
@authApi.get("/getusercreds")
async def getUserCredentials(data: UserName = Depends(), current_user: str = Depends(get_current_user)):
    """
    Retrieves user credentials, including their API key.
    Args:
        data (UserName): The username provided as dependency-injected data.
    Returns:
        JSONResponse: A response containing the user's credentials.
    """
    try:
        with flask_app.app_context():
            user = User.query.filter_by(username=data.username).first()  # Find the user by username
            if user == None:
                raise HTTPException(detail=f"User name does not exist (User logged in with invalid username, critical security issue)", status_code=400)
            api_key = API_key.query.filter_by(assigned_to=user.user_id).first()  # Find the API key for the user
            form_data = {
                "username": user.username,  # Include the username
                "api_key": api_key.key     # Include the API key
            }
            return JSONResponse(content={"params": form_data}, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"message":f"{e.detail}"}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content={"message":f"An internal error occurred: {e}"}, status_code=500)


#Validate refresh token (normally this will be called once, after a long time of user inactivity)
@authApi.post("/validateSession")
async def validateSession(username: str = Form(...),refreshToken: str = Depends(get_current_user2)):   #Current_user is actualy refresh token being passed from frontend 
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    if username != refreshToken:
        raise credentials_exception
    try :
        return JSONResponse(content={"message" : "Session active!"})
    except Exception as e:
        return JSONResponse(content={"message": f"An internal error occurred: {e}"}, status_code=500)
    

#Refresh jwtoken with refresh token
@authApi.post("/refreshjwtoken")
async def refreshJWToken(username: str = Form(...),refreshToken: str = Depends(get_current_user2)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    if username != refreshToken:
        raise credentials_exception
    try:
        new_token =  create_access_token(data={"sub": username})
        return JSONResponse(content={"message": "jwtoken refreshed", "access_token": new_token,
                                            "token_type" : "bearer"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"An internal error occurred: {e}"}, status_code=500)