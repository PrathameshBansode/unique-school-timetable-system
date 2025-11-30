from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask import jsonify
from models.course import Course
from werkzeug.security import generate_password_hash
from models.student import student_courses
from models.subject import Subject
from models.room import Room
from models.timetable import Timetable
from models.teacher import Teacher
from models.student import Student
from services.generate import generate_random_schedule
from models import User, UserRole, Student, Course
from flask import request, redirect, flash, url_for, render_template
from models.user import User, UserRole # <-- Added this import
from sqlalchemy import text
from app import db
from models.user import UserRole
import json

management_bp = Blueprint('management', __name__, url_prefix='/manage')

@management_bp.before_request
@login_required
def restrict_to_admin():
    if current_user.role != UserRole.ADMIN:
        return "Unauthorized", 403

# ------------------ Teachers ------------------
@management_bp.route('/teachers', endpoint='teachers')
def teachers():
    all_teachers = Teacher.query.all()
    return render_template('management/teachers.html', teachers=all_teachers)

# ------------------ Add Teacher ------------------
@management_bp.route('/teacher/add', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        max_weekly_hours = request.form['max_weekly_hours']
        availability = request.form['availability']
        vacation_days = request.form['vacation_days']
        username = request.form['username']
        password = request.form['password']

        # Validate fields (ensure they are not empty)
        if not name or not max_weekly_hours or not availability or not vacation_days or not username or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('management.add_teacher'))

        try:
            availability = json.loads(availability)
            vacation_days = json.loads(vacation_days)
        except json.JSONDecodeError:
            flash("Invalid JSON format for availability or vacation days", "danger")
            return redirect(url_for('management.add_teacher'))

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Choose a different one.", "danger")
            return redirect(url_for('management.add_teacher'))

        # ✅ Create new user (password will be hashed in model)
        new_user = User(
            role=UserRole.TEACHER,
            username=username,
            email=f"{username}@school.com",
            password=password  # <-- pass raw password
        )

        db.session.add(new_user)
        db.session.commit()

        # Create teacher record
        new_teacher = Teacher(
            name=name,
            max_hours_week=max_weekly_hours,
            availability=json.dumps(availability),
            vacation_days=json.dumps(vacation_days),
            user_id=new_user.id
        )

        db.session.add(new_teacher)
        db.session.commit()

        flash("Teacher added successfully", "success")
        return redirect(url_for('management.teachers'))

    return render_template('management/add_teacher.html')

# ------------------ Students ------------------
@management_bp.route('/students', endpoint='students')
def students():
    # Fetch all students from the database
    all_students = Student.query.all()  # Define all_students variable
    return render_template('management/students.html', students=all_students)

# --------------------------------------------------------------------------
@management_bp.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already in use. Please choose a different email.", "danger")
            return redirect(url_for('management.add_student'))  # Redirect to the same page if email exists

        # Check if the username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash("Username already in use. Please choose a different username.", "danger")
            return redirect(url_for('management.add_student'))  # Redirect to the same page if username exists

        # Create a new user with the provided details
        new_user = User(name=name, email=email, username=username, password=password, role=UserRole.STUDENT)
        db.session.add(new_user)
        db.session.commit()

        # Create a student and associate it with the new user
        new_student = Student(
            name=name,
            email=email,
            user_id=new_user.id  # Assign the user_id to the student
        )
        
        # Add student to the session (but don't commit yet)
        db.session.add(new_student)

        # Get the selected course IDs from the form (this will be a list)
        selected_courses = request.form.getlist('courses')  # Fetch the selected courses as a list of IDs

        # Add student to each selected course
        for course_id in selected_courses:
            course = Course.query.get(course_id)
            if course:
                # Avoiding duplicate student-course pairing
                if course not in new_student.enrolled_courses:
                    new_student.enrolled_courses.append(course)

        # Commit the changes
        db.session.commit()

        flash("Student added successfully", "success")
        return redirect(url_for('management.students'))

    # Fetch all available courses to display in the form
    all_courses = Course.query.all()
    return render_template('management/add_student.html', courses=all_courses)

# ------------------ Edit Student ------------------
@management_bp.route('/student/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)  # Fetch student by ID

    if request.method == 'POST':
        # Update student data with the form data
        student.name = request.form['name']
        student.email = request.form['email']
        db.session.commit()  # Commit the changes to the database
        flash("Student updated successfully", "success")
        return redirect(url_for('management.students'))  # Redirect to the students page

    return render_template('management/edit_student.html', student=student)  # Render the edit page

# ------------------ Delete Student ------------------
@management_bp.route('/student/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully", "success")
    return redirect(url_for('management.students'))
# ------------------ Courses ------------------
@management_bp.route('/courses', endpoint='courses')
def courses():
    all_courses = Course.query.all()
    return render_template('management/courses.html', courses=all_courses)

# ------------------ Add Course ------------------
@management_bp.route('/add-course', methods=['GET', 'POST'], endpoint='add_course')
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        credits = request.form['credits']
        course_type = request.form['type']
        hours = request.form['hours']

        new_course = Course(
            name=name,
            credits=credits,
            type=course_type,
            subject_hours=hours
        )

        db.session.add(new_course)
        db.session.commit()
        flash("Course added successfully", "success")
        return redirect(url_for('management.courses'))

    return render_template('management/add_course.html')

# ------------------ Delete Course ------------------
@management_bp.route('/delete-course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted successfully", "success")
    return redirect(url_for('management.courses'))

# ------------------ Add Subject ------------------
# ------------------ Add Subject and List Subjects ------------------
@management_bp.route('/subject/add', methods=['GET', 'POST'], endpoint='add_subject')
def add_subject():
    if request.method == 'POST':
        name = request.form['name']
        course_id = request.form['course_id']
        teacher_id = request.form['teacher_id']
        hours = request.form['hours']
        subject_type = request.form['type']  # Get the type field from the form

        # Debugging: Check if the form data is received
        print(f"Received form data: {name}, {course_id}, {teacher_id}, {hours}, {subject_type}")

        # Validate that the course and teacher exist
        course = Course.query.get(course_id)
        teacher = Teacher.query.get(teacher_id)

        if not course:
            flash("Invalid Course ID", "danger")
            return redirect(url_for('management.add_subject'))

        if not teacher:
            flash("Invalid Teacher ID", "danger")
            return redirect(url_for('management.add_subject'))

        try:
            # Create new subject with type
            new_subject = Subject(
                name=name,
                course_id=course_id,
                teacher_id=teacher_id,
                hours_per_week=hours,
                type=subject_type  # Pass the type field
            )

            db.session.add(new_subject)
            db.session.commit()
            flash("Subject added successfully", "success")
        except Exception as e:
            # Handle database commit errors
            flash(f"Error: {str(e)}", "danger")

    # Fetch courses, teachers, and subjects for the form and list
    all_courses = Course.query.all()
    all_teachers = Teacher.query.all()
    all_subjects = Subject.query.all()

    return render_template('management/add_subject.html', courses=all_courses, teachers=all_teachers, subjects=all_subjects)

#-----------------------------------------------------
@management_bp.route('/get_courses_and_teachers', methods=['GET'])
def get_courses_and_teachers():
    courses = Course.query.all()
    teachers = Teacher.query.all()

    # Create lists of dictionaries for courses and teachers
    courses_data = [{'id': course.id, 'name': course.name} for course in courses]
    teachers_data = [{'id': teacher.id, 'name': teacher.name} for teacher in teachers]

    # Return the data as JSON
    return jsonify({'courses': courses_data, 'teachers': teachers_data})

#-----------------------------------------------------
# ------------------ Subjects List ------------------
@management_bp.route('/subjects', endpoint='subjects')  # Correct the endpoint
def subjects():
    all_subjects = Subject.query.all()
    return render_template('management/subjects.html', subjects=all_subjects)

# ------------------ Rooms ------------------
@management_bp.route('/rooms', endpoint='rooms')
def rooms():
    all_rooms = Room.query.all()
    return render_template('management/rooms.html', rooms=all_rooms)

@management_bp.route('/room/add', methods=['POST'])
def add_room():
    name = request.form['name']
    capacity = request.form['capacity']
    rtype = request.form['type']
    new_room = Room(name=name, capacity=capacity, type=rtype)
    db.session.add(new_room)
    db.session.commit()
    flash("Room added successfully", "success")
    return redirect(url_for('management.rooms'))

# ------------------ Timetable ------------------

@management_bp.route('/generate_timetable', endpoint='generate_timetable', methods=['GET', 'POST'])
def generate_timetable():
    if request.method == 'POST':
        # Trigger the timetable generation using the genetic algorithm
        count = generate_random_schedule()  # Call function in generate.py
        flash(f"Timetable generated successfully! {count} entries created.", "success")
        return redirect(url_for('management.view_timetable'))
    
    # If GET request, render the timetable generation form
    return render_template('timetable/generate_timetable.html')
from datetime import time

@management_bp.route('/view_timetable', endpoint='view_timetable')
def view_timetable():
    timetables = Timetable.query.all()

    # Define the days of the week and time slots
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    time_slots = [
        '10:00 AM - 11:00 AM', '11:00 AM - 12:00 PM', '12:00 PM - 01:00 PM',
        '01:00 PM - 02:00 PM', '02:00 PM - 03:00 PM', '03:00 PM - 04:00 PM'
    ]
    
    # Initialize a dictionary to store timetable entries
    timetable = {day: {time_slot: None for time_slot in time_slots} for day in days}

    # Group timetable entries by day and time slot
    for entry in timetables:
        day_of_week = entry.day_of_week
        start_time_str = entry.start_time.strftime('%I:%M %p')
        end_time_str = entry.end_time.strftime('%I:%M %p')
        time_slot = f'{start_time_str} - {end_time_str}'

        if time_slot in timetable[day_of_week]:
            timetable[day_of_week][time_slot] = entry

    return render_template('management/view_timetable.html', timetable=timetable, days=days, time_slots=time_slots)

from flask import render_template, request, redirect, url_for, flash
from models.timetable import Timetable
from models.course import Course
from models.teacher import Teacher
from models.subject import Subject
from models.room import Room
from app import db

from datetime import datetime, time
# ------------------ Timetable ------------------
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from app import db
from models import Timetable, Subject, Teacher, Course, Room  # Ensure to import necessary models

@management_bp.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        course_id = request.form['course_id']
        subject_id = request.form['subject_id']
        teacher_id = request.form['teacher_id']
        room_id = request.form['room_id']
        day = request.form['day']
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        student_group = request.form['student_group']

        # Convert start_time and end_time to Python time objects
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()  # Convert to time object
            end_time = datetime.strptime(end_time_str, '%H:%M').time()  # Convert to time object
        except ValueError:
            flash("Invalid time format. Please use the format HH:MM.", "danger")
            return redirect(url_for('management.add_entry'))

        # Check for Teacher Conflict if checkbox is checked
        check_teacher_conflict = 'check_teacher_conflict' in request.form
        if check_teacher_conflict:
            conflicting_teacher = Timetable.query.filter(
                Timetable.teacher_id == teacher_id,
                Timetable.day_of_week == day,
                Timetable.start_time < end_time,
                Timetable.end_time > start_time
            ).first()
            if conflicting_teacher:
                flash(f"Teacher {conflicting_teacher.teacher.name} is already scheduled for this time.", "danger")
                return redirect(url_for('management.add_entry'))

        # Check for Room Conflict if checkbox is checked
        check_room_conflict = 'check_room_conflict' in request.form
        if check_room_conflict:
            conflicting_room = Timetable.query.filter(
                Timetable.room_id == room_id,
                Timetable.day_of_week == day,
                Timetable.start_time < end_time,
                Timetable.end_time > start_time
            ).first()
            if conflicting_room:
                flash(f"Room {conflicting_room.room.name} is already booked for this time.", "danger")
                return redirect(url_for('management.add_entry'))

        # If conflicts are unchecked, automatically allocate the next available slot
        if not check_teacher_conflict and not check_room_conflict:
            available_slot = Timetable.query.filter(
                Timetable.teacher_id == teacher_id,
                Timetable.room_id == room_id,
                Timetable.day_of_week == day,
                Timetable.start_time >= start_time
            ).order_by(Timetable.start_time).first()

            if available_slot:
                # Found an available slot, use it for this timetable entry
                start_time = available_slot.start_time
                end_time = available_slot.end_time
            else:
                # No available slot, flash a message
                flash(f"No available slot found for teacher {teacher_id} and room {room_id} on {day}.", "danger")
                return redirect(url_for('management.add_entry'))

        # Create and add new timetable entry if no conflicts
        timetable_entry = Timetable(
            course_id=course_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            room_id=room_id,
            day_of_week=day,
            start_time=start_time,
            end_time=end_time,
            student_group=student_group
        )

        db.session.add(timetable_entry)
        db.session.commit()

        flash("Timetable entry added successfully!", "success")
        return redirect(url_for('management.view_timetable'))

    # If GET request, render the add entry form
    courses = Course.query.all()
    subjects = Subject.query.all()
    teachers = Teacher.query.all()
    rooms = Room.query.all()
    return render_template('management/timetable_form.html', courses=courses, subjects=subjects, teachers=teachers, rooms=rooms)

# -----------------------------------------------------------------------------------
from flask import Response
from io import BytesIO
from fpdf import FPDF
from models.timetable import Timetable

@management_bp.route('/export_pdf', methods=['GET'])
def export_pdf():
    timetables = Timetable.query.all()  # Get all timetables from the DB

    # Create a PDF instance
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add title to the PDF
    pdf.cell(200, 10, txt="Timetable Report - Unique School", ln=True, align="C")

    # Add table headers (columns for the timetable)
    pdf.cell(40, 10, txt="Day", border=1)
    pdf.cell(30, 10, txt="Start Time", border=1)
    pdf.cell(30, 10, txt="End Time", border=1)
    pdf.cell(60, 10, txt="Course", border=1)
    pdf.cell(60, 10, txt="Teacher", border=1)
    pdf.ln()

    # Iterate through timetable entries and add them to the PDF
    for entry in timetables:
        pdf.cell(40, 10, txt=entry.day_of_week, border=1)
        pdf.cell(30, 10, txt=entry.start_time.strftime('%H:%M'), border=1)
        pdf.cell(30, 10, txt=entry.end_time.strftime('%H:%M'), border=1)
        pdf.cell(60, 10, txt=entry.course.name, border=1)
        pdf.cell(60, 10, txt=entry.teacher.name, border=1)
        pdf.ln()

    # Create a BytesIO object to hold the PDF content in memory
    pdf_output = BytesIO()
    
    # Output the PDF to the BytesIO object
    pdf.output(pdf_output, 'F')
    
    # Seek back to the beginning of the BytesIO object
    pdf_output.seek(0)

    # Debugging: Check the length of the generated PDF data
    pdf_data = pdf_output.getvalue()
    print(f"Generated PDF length: {len(pdf_data)} bytes")

    # Ensure response is correct and send the PDF to the browser as an attachment
    try:
        return Response(pdf_data, content_type='application/pdf', 
                        headers={"Content-Disposition": "attachment; filename=Timetable_Report.pdf"})
    except Exception as e:
        print("Error generating PDF:", e)
        return "Error generating PDF", 500

# -------------------------------------------------------------------------------------------
from flask import Response
from io import BytesIO
import pandas as pd  # For Excel export
from models.timetable import Timetable

from flask import Response
from io import BytesIO
import pandas as pd  # For Excel export
from models.timetable import Timetable
from flask import Response
from io import BytesIO
import pandas as pd  # For Excel export
from models.timetable import Timetable

# Export to Excel
@management_bp.route('/export_excel', methods=['GET'])
def export_excel():
    timetables = Timetable.query.all()

    # Define the days of the week and time slots
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    time_slots = [
        '10:00 AM - 11:00 AM', '11:00 AM - 12:00 PM', '12:00 PM - 01:00 PM',
        '01:00 PM - 02:00 PM', '02:00 PM - 03:00 PM', '03:00 PM - 04:00 PM'
    ]

    # Initialize a dictionary to store timetable entries in the required format
    timetable = {time_slot: {day: None for day in days} for time_slot in time_slots}

    # Group timetable entries by day and time slot
    for entry in timetables:
        day_of_week = entry.day_of_week
        start_time_str = entry.start_time.strftime('%I:%M %p')
        end_time_str = entry.end_time.strftime('%I:%M %p')
        time_slot = f'{start_time_str} - {end_time_str}'
        
        if time_slot in timetable:
            timetable[time_slot][day_of_week] = entry

    # Create a list of rows for Excel
    excel_data = []
    excel_data.append(['Time / Day'] + days)  # Header row

    for time_slot in time_slots:
        row = [time_slot]  # Start with the time slot in the first column
        for day in days:
            entry = timetable[time_slot][day]
            if entry:
                # Prepare timetable details in the required format
                subject_details = f"{entry.subject.name}\n{entry.subject.type}\n{entry.teacher.name}\n{entry.room.name}\n{entry.student_group}"
                row.append(subject_details)
            else:
                row.append("No class")
        excel_data.append(row)

    # Create a DataFrame
    df = pd.DataFrame(excel_data)

    # Export to Excel
    output = BytesIO()
    df.to_excel(output, index=False, header=True)
    output.seek(0)
    return Response(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
