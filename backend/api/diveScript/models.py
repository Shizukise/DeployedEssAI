from backend.app import db
from sqlalchemy import ForeignKey
from .utils import teams, matieres

##Specific matieres database classes

class SpecificArticle(db.Model):

    
    """
    Each object will hold its name, quantity and team it belongs to 
    Quantity will in 2 different ways, to be summed and render the value between orders, and to be rendered with the quantity for each order
    The team will be assigned depending on the department where this order will be sent to (aplication/enterprise specific)
    Departments are assigned a number from 100 to 132. Each team holds a number of this deparments
    """

    __tablename__ = 'specific_articles'
    id = db.Column(db.Integer(), unique=True, primary_key=True)
    article_name = db.Column(db.String(), nullable=False)
    article_quantity = db.Column(db.Integer(), nullable=False)
    order_CO = db.Column(db.String(), nullable=False)
    href = db.Column(db.String(),nullable=False)
    team = db.Column(db.String(), nullable=False, default="")
    department = db.Column(db.Integer(), nullable=False, default=0)
    matiere = db.Column(db.String, default="Diver") 
    
    def setTeam(self):
        self.team = teams[self.department]

    def setMatiere(self):
        normalized_article_name = self.article_name.lower().replace(" ", "")
        self.matiere = [i for i in matieres if i.replace(" ", "").lower() in normalized_article_name]
        
        if not self.matiere:
            self.matiere = "Diver"
        else:
            self.matiere = self.matiere[0]  # Take the first match if multiple

