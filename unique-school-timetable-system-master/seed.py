from app import create_app, db
from models.user import User, UserRole
from models.teacher import Teacher
from models.student import Student
from models.course import Course
from models.subject import Subject
from models.room import Room
from models.timetable import Timetable
from datetime import datetime

app = create_app()

with app.app_context():
    # Drop all tables and create new ones
    db.drop_all()
    db.create_all()

    # Create users (admin, teacher, and student)
    admin_user = User(username='admin', password='admin', role=UserRole.ADMIN)
    teacher_user = User(username='teacher1', password='teacher1', role=UserRole.TEACHER)
    student_user = User(username='student1', password='student1', role=UserRole.STUDENT)

    db.session.add_all([admin_user, teacher_user, student_user])
    db.session.commit()

    # Create teacher and student profiles
    # teacher = Teacher(
    #     user_id=teacher_user.id, 
    #     name='John Doe', 
    #     email='john.doe@example.com', 
    #     max_hours_week=10, 
    #     availability='{"Monday": ["10:00 AM - 11:00 AM"]}', 
    #     vacation_days='["2025-12-25"]'
    # )
    # student = Student(
    #     user_id=student_user.id, 
    #     name='Jane Smith', 
    #     email='jane.smith@example.com'
    # )

    # db.session.add_all([teacher, student])
    # db.session.commit()

    # # Create courses and rooms
    # course = Course(
    #     name='Computer Science', 
    #     credits=3,  
    #     type='Lecture',  
    #     subject_hours=40,  
    #     description='BSc in CS'
    # )

    # room = Room(name='Room 101', capacity=30, type='Classroom') 

    # db.session.add_all([course, room])
    # db.session.commit()

    # Create subject and link it to the course and teacher
    # subject = Subject(
    #     name='Python Programming', 
    #     course_id=course.id, 
    #     teacher_id=teacher.id,
    #     hours_per_week=5  # Ensure this value is passed
    # )

    # db.session.add(subject)
    # db.session.commit()

    # Convert the string times to time objects
    # start_time = datetime.strptime('10:00 AM', '%I:%M %p').time()
    # end_time = datetime.strptime('11:00 AM', '%I:%M %p').time()

    # Create timetable entry and link it to the course, subject, teacher, and room
    # timetable = Timetable(
    #     course_id=course.id,
    #     subject_id=subject.id,
    #     teacher_id=teacher.id,
    #     room_id=room.id,
    #     day_of_week='Monday',
    #     start_time=start_time,
    #     end_time=end_time
    # )

    # db.session.add(timetable)
    # db.session.commit()

    print("✅ Seed data inserted successfully!")
