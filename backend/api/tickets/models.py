from backend.app import db
from sqlalchemy import ForeignKey
import os,subprocess,platform
from pathlib import Path

class Ticket(db.Model):
    """
    Tickets data table
    Title is also the name of created folders. For each open ticket, there is a folder with its ticket title as name.
    Anytime a folder path is needed, it can be retrieved with this title.
    Relationship with the user that creates the files that need modification, hence the opening of a ticket."""
    __tablename__ = 'tickets'
    ticket_id = db.Column(db.Integer(), unique=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100),nullable=False)
    assigned_to = db.Column(db.Integer(), ForeignKey('users.user_id'), nullable=False)

    def openTicketFolder(self):
        """
        This method to be called whenever an endpoint needs to open
        the ticket folder
        """
        try:
          try:
            path = Path(f"../OpenTickets/{self.title}")
            if os.path.exists(path):
                if platform.system() == "Windows":
                    os.startfile(path)  # Works for Windows
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", path])
                else:  # Linux and others
                    subprocess.run(["xdg-open", path])
                return 200,{"message":"Ticket folder opened!"}
            else:
              raise ValueError
          except ValueError:
            return 404,{"message":"Ticket not found!:"}  
        except Exception:
          return 500,{"message":"An internal error occurred"}
