from app import db
import json
from models.course import Course
from models.subject import Subject
from models.teacher import Teacher
from models.room import Room  # Ensure to import the Room model if needed

class Timetable(db.Model):
    __tablename__ = 'timetables'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)

    day_of_week = db.Column(db.Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', name='days'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    student_group = db.Column(db.Text, nullable=True)  # JSON: list of student IDs or group info

    # Relationships
    course = db.relationship('Course', backref='timetable_entries')
    subject = db.relationship('Subject', backref='timetable_entries')
    teacher = db.relationship('Teacher', backref='timetable_entries')
    room = db.relationship('Room', back_populates='timetables')  # Ensure Room is properly set up

    def get_students(self):
        """
        Returns a list of students (or groups) based on the student_group field.
        The student_group field is expected to be a JSON string that can be parsed into a list.
        If the student_group field is empty or invalid, an empty list is returned.
        """
        if self.student_group:
            try:
                return json.loads(self.student_group)  # Try to parse JSON if it's not empty
            except json.JSONDecodeError:
                return []  # If there's an error in decoding, return an empty list
        return []  # Return empty list if student_group is None or empty

    def get_class_duration(self):
        """
        Returns the duration of the class based on the course type (Theory or Lab).
        - 1 hour for Theory classes
        - 2 continuous hours for Lab classes
        """
        if self.subject:
            if self.subject.name.lower() == 'lab':  # Check if it's a Lab subject
                return 2  # Return 2 hours for lab
            else:
                return 1  # Return 1 hour for theory
        return 1  # Default to 1 hour if no subject type is defined
