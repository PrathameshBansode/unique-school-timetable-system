from app import db
import json

class Constraint(db.Model):
    __tablename__ = 'constraints'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)  # e.g., 'room_capacity', 'max_hours'
    details = db.Column(db.Text, nullable=False)  # JSON: custom structure per type

    def get_details(self):
        return json.loads(self.details)
