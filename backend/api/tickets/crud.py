from .models import Ticket
import shutil
from pathlib import Path
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
""" Basic CRUD endpoints """



test_api_router = APIRouter()

@test_api_router.get("/api/test")
def test_endpoint():
    return {"message": "This is a test endpoint!"}


ticket_api = APIRouter(prefix="/api/tickets")

class TicketRequest(BaseModel):
    """Pydantic validations"""
    api_key : str
    order_number : int
    PDFstring: str
    description: str

@ticket_api.post("/create")
def open_ticket(data: TicketRequest):
    try:
        from backend.app import app,db        
        with app.app_context():
            print("hello world")

            return {"message": "Ticket successfully opened"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
