from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.teacher import Teacher
from models.user import UserRole
from models.timetable import Timetable
from app import db
import json
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Dashboard Home Route
@dashboard_bp.route('/')
@login_required
def home():
    print(f"Current User: {current_user.username}, Role: {current_user.role}")  # Debugging print

    if current_user.role == UserRole.ADMIN:
        return render_template('dashboards/admin_dashboard.html')
    elif current_user.role == UserRole.TEACHER:
        return redirect(url_for('dashboard.teacher_dashboard'))
    elif current_user.role == UserRole.STUDENT:
        return render_template('dashboards/student_dashboard.html')
    elif current_user.role == UserRole.STAFF:
        return render_template('dashboards/staff_dashboard.html')
    else:
        return "Unauthorized", 403

# Teacher Dashboard Route
@dashboard_bp.route('/teacher', methods=['GET', 'POST'])
@login_required
def teacher_dashboard():
    print(f"Current User: {current_user.name}")  # Debugging print

    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        flash('Teacher not found!', 'danger')
        return redirect(url_for('login'))

    timetable = get_teacher_timetable(teacher)
    vacation_days = teacher.get_vacations()

    return render_template('dashboards/teacher_timetable.html', timetable=timetable, vacation_days=vacation_days)


# Fetch the teacher's specific timetable
def get_teacher_timetable(teacher):
    timetable_data = Timetable.query.filter_by(teacher_id=teacher.id).all()

    timetable = {}
    for entry in timetable_data:
        day_of_week = entry.day_of_week
        start_time = entry.start_time.strftime('%I:%M %p')
        end_time = entry.end_time.strftime('%I:%M %p')
        time_slot = f"{start_time} - {end_time}"

        if day_of_week not in timetable:
            timetable[day_of_week] = {}

        timetable[day_of_week][time_slot] = {
            'subject': entry.subject.name,
            'professor': entry.teacher.name,
            'room': entry.room.name
        }

    print("Formatted Timetable:", timetable)  # Debugging print

    return timetable

# Function to add vacation day to the teacher's profile
def add_vacation_day(teacher, vacation_day):
    vacation_days = teacher.get_vacations()
    vacation_days.append(vacation_day)
    teacher.vacation_days = json.dumps(vacation_days)
    db.session.commit()
