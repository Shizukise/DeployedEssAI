from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import os
from backend.core.utils import FileOperator
from backend.api.validations.validations import Validations
from pydantic import BaseModel
from backend.app import app as flask_app
from backend.core.database import API_key

#Every morning a scraper should run an retrieve every Invoice file for every command till date. 
#It's most likely that an order created one day, wont be sent to production the same day
#If this is called in the creation process, or BAT1, the invoice should be inputed by the user

#Also, for each user action, an api call should be recorded and logged with the user api key, to keep track of user action and block ddos for example,
#by blocking multiple consequent equal actions



UPLOAD_FOLDER = "/home/galopin/project_root/backend/core/data/ToValidate" 

fo = FileOperator()
val = Validations()
validation_api = APIRouter(prefix="/api/validation")

class ValidationCreate(BaseModel):
    files: list[UploadFile] = File(...)
    username: str = Form(str)
    api_key: str = Form(str)

##Authorization configs and imports
from backend.api.auth.auth import  get_current_user

@validation_api.post('/create')
async def createValidation(validation_args: ValidationCreate = Depends(), current_user: str = Depends(get_current_user)):
    print(f"Files: {validation_args.files}")
    print(f"Username: {validation_args.username}")
    print(f"API Key: {validation_args.api_key}")

    try:
        with flask_app.app_context():
            valid = [key.key for key in API_key.query.all()]
            if validation_args.api_key not in valid:
                raise HTTPException(status_code=401, detail="Unauthorized access")

        if not validation_args.files:
            raise HTTPException(status_code=400, detail="No file part in the request")

        allowed_types = ["application/pdf"]
        if not all(file.content_type in allowed_types for file in validation_args.files):
            raise HTTPException(status_code=400, detail="One or more files have unsupported types. Only PDF files are allowed.")

        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        for file in validation_args.files:
            if file.filename == '':
                raise HTTPException(status_code=400, detail="No file selected")
            # Save file to the UPLOAD_FOLDER
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            with open(filepath, "wb") as f:
                f.write(await file.read())
        return JSONResponse(content={"message": "Files uploaded successfully"}, status_code=200)

    except HTTPException as e:
        return JSONResponse(content={"message": e.detail}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content={"message": f"Unexpected error: {str(e)}"}, status_code=500)


@validation_api.post("/validate")
async def validateValidation():  #user : str, api_key :str
    """
    This is where all the validations will happen.
    This api call comes after the Call**1
    Here no input is expected from the user, when the user
    calls this method, all validations functions will be ran
    in the files stored in the middle folder (UPLOAD_FOLDER)
    """

    formats_quantities = {}
    types_quantities = {}
    failed_validations = {}

    for file in os.listdir(UPLOAD_FOLDER):
        """For each file we will store information about it like
            format, type (app specific, type of pdf drawing)
            and direct validations may be called in this loop
        """
        filepath = os.path.join(UPLOAD_FOLDER, file)
        print(filepath)
        file_format = fo.get_format(filepath)
        file_type = fo.get_type(filepath)
        vei_test = val.VEIvalidation(filepath)
        if not vei_test:
            failed_validations[f"{file}"] = "VEI quantity error"  #I WAS HERE
        if file_format not in formats_quantities:
            formats_quantities[file_format] = 1
        else:
            formats_quantities[file_format] += 1
        if file_type not in types_quantities:
            types_quantities[file_type] = 1
        else:
            types_quantities[file_type] += 1

    if len(failed_validations) != 0:
        """
        If any validation fails. "Validation" will be created with status = invalid.
        In an invalid validation page user will have the oportunity to regulate files
        and try to validate the files once again.
        """
        return JSONResponse(content={"message" : f"Some tests failed: {failed_validations}"}, status_code=200)
    return JSONResponse(content={"message": "Validated!"}, status_code=200)