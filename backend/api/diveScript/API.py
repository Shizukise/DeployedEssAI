from fastapi import APIRouter,HTTPException,Depends, Form
from fastapi.responses import JSONResponse
from backend.api.auth.auth import get_current_user
from backend.api.diveScript.diveScript import DiverScraper
from backend.app import app,db
from backend.api.diveScript.models import SpecificArticle
from backend.core.database import User, API_key
from pydantic import BaseModel


import pandas as pd
import os

DiveAPI = APIRouter(prefix="/api/dive")

from pathlib import Path

# Get the current directory (backend folder)
backend_dir = Path(__file__).resolve().parent


# Define the output folder path relative to the backend directory   
output_folder = backend_dir /  "rapport_out"  #For now it will work, later should be downloaded to user browser or desktop (or whatever he might decide to)

# Check if the directory exists, if not, create it
output_folder.mkdir(parents=True, exist_ok=True)

@DiveAPI.post("/divein")
async def diveIn(current_user: str = Depends(get_current_user), api_key : str = Form(...), username : str = Form(...), password : str = Form(...)):
    try:
        credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
        diver = DiverScraper(username="Atelier",password=password)
        data = diver.run_script()
        print(data)
        with app.app_context():
            user = User.query.filter_by(username=username).first()
            apikey = API_key.query.filter_by(key=api_key).first()    
            if user.user_id != apikey.assigned_to:
                raise credentials_exception
            data_list = []
            existing_CO = set([item.order_CO for item in SpecificArticle.query.all()])
            for commande in data:
                data_list.append(commande["Référence"])
                for article in commande["Articles Spécifiques"]:
                    if commande['Référence'] in existing_CO:
                        continue
                    newItem = SpecificArticle(article_name=article['Description'],article_quantity=article['Quantité'],order_CO=commande['Référence'],
                                            href=commande['HREF'],department=int(commande['Department'][:3]))
                    newItem.setTeam()
                    newItem.setMatiere()
                    db.session.add(newItem)
            db.session.commit()
            for co in existing_CO:
                if co not in data_list:
                    to_delete = SpecificArticle.query.filter_by(order_CO=co).first()
                    db.session.delete(to_delete)
            db.session.commit()
        return JSONResponse(content={"message": data}, status_code=200)
    except Exception as e:
        print("error",e)
        return JSONResponse(content={"message":f"An internal error occurred {e}"}, status_code=500)



@DiveAPI.post("/diveout")
async def diveOut(username: str = Form(...),current_user: str = Depends(get_current_user)):
    """
    For now it is creating an xls file, but later should create all comma separated files, excels and prioritarily, pdfs.
    This endpoint calls the database for all stored data and outputs the user with desired data.
    Also it should take filters (TECHNICAL DEBT HERE)
    """

    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        with app.app_context():
            if username != current_user:
                raise credentials_exception
            # Fetch all SpecificArticle objects
            data = SpecificArticle.query.all()
            # Convert SQLAlchemy objects to a list of dictionaries
            data_dict = [
                {
                    "ID": article.id,
                    "Article Name": article.article_name,
                    "Quantity": article.article_quantity,
                    "Order CO": article.order_CO,
                }
                for article in data
            ]

            # Create a DataFrame from the dictionary
            df = pd.DataFrame(data_dict)

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)  # Create the directory if it doesn't exist


            file_name = "rapport_commandes_specifiques.xlsx"
            file_path = os.path.join(output_folder, file_name)

            # Write the DataFrame to an Excel file
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Commandes")
                workbook = writer.book
                worksheet = writer.sheets["Commandes"]

                # Auto-adjust column widths
                for idx, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    column_letter = worksheet.cell(row=1, column=idx + 1).column_letter
                    worksheet.column_dimensions[column_letter].width = max_len

            # Return success response
            return JSONResponse(content={"message": "Excel file created successfully."}, status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


class Filters(BaseModel) :
    agence : str = Form(...)
    team : str = Form(...)


@DiveAPI.get('/fetchall')
async def fetchAll(team : str, agence : str, current_user: str = Depends(get_current_user)):
    if team == "Tous" and agence == "Tous":
        try:
            with app.app_context():
                data = SpecificArticle.query.all()
                data_dict = [
                        {
                            "ID": article.id,
                            "Article Name": article.article_name,
                            "Quantity": article.article_quantity,
                            "Order CO": article.order_CO,
                            'href': article.href,
                            'Team': article.team,
                            'Agence': article.department
                        }
                        for article in data
                    ]
                return JSONResponse(content={"data":data_dict}, status_code=200)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    elif team == "Tous" and agence != "Tous":
        try:
            with app.app_context():
                data = SpecificArticle.query.all()
                data_dict = [
                        {
                            "ID": article.id,
                            "Article Name": article.article_name,
                            "Quantity": article.article_quantity,
                            "Order CO": article.order_CO,
                            'href': article.href,
                            'Team': article.team,
                            'Agence': article.department
                        }
                        for article in data if article.department == int(agence)
                    ]
                return JSONResponse(content={"data":data_dict}, status_code=200)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    elif team != "Tous" and agence == "Tous":
        try:
            with app.app_context():
                data = SpecificArticle.query.all()
                data_dict = [
                        {
                            "ID": article.id,
                            "Article Name": article.article_name,
                            "Quantity": article.article_quantity,
                            "Order CO": article.order_CO,
                            'href': article.href,
                            'Team': article.team,
                            'Agence': article.department
                        }
                        for article in data if article.team == team
                    ]
                return JSONResponse(content={"data":data_dict}, status_code=200)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    else:
        try:
            with app.app_context():
                data = SpecificArticle.query.all()
                data_dict = [
                        {
                            "ID": article.id,
                            "Article Name": article.article_name,
                            "Quantity": article.article_quantity,
                            "Order CO": article.order_CO,
                            'href': article.href,
                            'Team': article.team,
                            'Agence': article.department
                        }
                        for article in data if article.team == team and article.department == int(agence)
                    ]
                return JSONResponse(content={"data":data_dict}, status_code=200)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)