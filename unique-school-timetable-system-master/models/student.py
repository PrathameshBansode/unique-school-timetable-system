# models/student.py

from app import db

# Association table for many-to-many relationship
student_courses = db.Table('student_courses',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Added this line
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    student_group = db.Column(db.String(50), nullable=True)

    # Relationship with User model
    user = db.relationship('User', backref='student')

    
    # Many-to-many relationship with Course model, avoiding duplicate student-course pairings
    enrolled_courses = db.relationship('Course', secondary=student_courses, backref=db.backref('students', lazy='dynamic'), lazy='dynamic', passive_deletes=True)

    def __repr__(self):
        return f'<Student {self.name}>'

