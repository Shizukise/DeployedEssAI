from backend.app import db
from pathlib import Path
from sqlalchemy import ForeignKey


class Validation(db.Model):
    
    """ Validation db model, This is one of the main components of this app flow.
        The best case scenario is a validation to be created with status = valid
        A sequence of validation functions will be run before creating a Validation instance,
        if one of these tests fails, it might be overwritten by user, with a logical explanation,
        else it will be created with a status = invalid
        Also, for the workflow of the workshop user role, any ticket opened will reference one of these
        Validation instances, and the user that validated it."""

    __tablename__ = "validations"

    validation_id = db.Column(db.Integer(), unique=True, primary_key=True)
    file_name = db.Column(db.String(50), unique=True, nullable=False)
    validation_status = db.Column(db.String(18), nullable=False)
    order_number = db.Column(db.String(50),unique=True,nullable=False)
    remark = db.Column(db.String(360), default = "")
    
    """Relationships"""
    
    "This relationship is important, as it will be called upon when creating a ticket by the workshop"
    validated_by = db.Column(db.Integer(), ForeignKey('users.user_id'), nullable=False)