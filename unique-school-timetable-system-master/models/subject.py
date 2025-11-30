from app import db

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    

    # Foreign keys
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)

    # Relationships
    course = db.relationship('Course', backref='subjects', lazy=True)
    teacher = db.relationship('Teacher', backref='subjects', lazy=True)

    # Updated type field to enforce Theory or Lab
    type = db.Column(db.Enum('Theory', 'Lab', 'Seminar', name='subject_types'), nullable=False)

    hours_per_week = db.Column(db.Integer, nullable=False)

    def __init__(self, name, course_id, teacher_id, hours_per_week, type):
        self.name = name
        self.course_id = course_id
        self.teacher_id = teacher_id
        self.hours_per_week = hours_per_week
        self.type = type

    def __repr__(self):
        return f'<Subject {self.name}>'
