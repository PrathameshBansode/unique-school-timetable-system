from app import db
import json
from models.subject import Subject  # Import the Subject model

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    # Teacher's fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to User table
    name = db.Column(db.String(100), nullable=False)  # Teacher's name
    email = db.Column(db.String(100), nullable=True)  # Teacher's email (optional)
    max_hours_week = db.Column(db.Integer, nullable=False)  # Max hours per week the teacher can teach
    availability = db.Column(db.Text, nullable=True)  # Availability of the teacher in JSON format (day -> time slots)
    vacation_days = db.Column(db.Text, nullable=True)  # List of vacation days (JSON format)

    # Relationships
    user = db.relationship('User', backref='teacher')

    def get_availability(self):
        return json.loads(self.availability) if self.availability else {}

    def get_vacations(self):
        return json.loads(self.vacation_days) if self.vacation_days else []

    def __repr__(self):
        return f'<Teacher {self.name}>'
