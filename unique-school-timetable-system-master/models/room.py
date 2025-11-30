from app import db

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Enum('Lecture', 'Lab', 'Classroom', 'Seminar', name='room_type'), nullable=False)

    # Back-reference to timetable entries
    timetables = db.relationship('Timetable', back_populates='room', cascade='all, delete-orphan')
