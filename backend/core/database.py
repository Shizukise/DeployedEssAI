from backend.app import db,bcrypt
from sqlalchemy import ForeignKey
from flask_login import UserMixin

""" 
Main data classes
Users
"""

class User(db.Model):
    """ username, password(will be hashed), user_role,team
    User class will be used to validate trough user roles, to filter trough
    user team and have a one on many relationship with Ticket model."""

    __tablename__ = 'users'
    user_id = db.Column(db.Integer(), unique=True, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    user_role = db.Column(db.String(18), nullable=False) 
    team = db.Column(db.String(32),nullable=False)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, unhashed_password):
        if not isinstance(unhashed_password,str):
            raise TypeError
        else:
            self.password_hash = bcrypt.generate_password_hash(unhashed_password).decode('utf-8')

    def password_authentication(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
    def get_id(self):
        return str(self.user_id)
    


class API_key(db.Model):

    __tablename__ = 'api_keys'
    id = db.Column(db.Integer(), unique=True, primary_key=True)
    key = db.Column(db.String(16), unique=True, nullable=False)
    
    #relationship with User 
    assigned_to = db.Column(db.Integer(), ForeignKey('users.user_id'), nullable=False)
