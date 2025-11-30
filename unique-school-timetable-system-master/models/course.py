from app import db

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Enum('Lecture', 'Lab', 'Seminar', name='course_type'), nullable=False)
    subject_hours = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)