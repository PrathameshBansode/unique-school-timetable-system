from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models.timetable import Timetable
from models.teacher import Teacher
from models.subject import Subject
from models.room import Room
from models.course import Course
from app import db
import datetime
import pandas as pd
from models.student import Student
from io import BytesIO
from weasyprint import HTML
from services.validation import validate_entry  # ✅ Correct import

timetable_bp = Blueprint('timetable', __name__, url_prefix='/timetable')

# ------------------ View Timetable ------------------
@timetable_bp.route('/view_timetable')
@login_required
def view_timetable():
    # Fetch all timetable entries
    timetables = Timetable.query.all()

    # Define the days of the week and time slots for the timetable view
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

    # Render the same template for both admin and student
    return render_template('timetable/view_timetable_unified.html', timetable=timetable, days=days, time_slots=time_slots)

# ------------------ Add Timetable Entry ------------------
@timetable_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_entry():
    if current_user.role != 'admin':
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        data = request.form
        try:
            start_time = datetime.datetime.strptime(data['start_time'], "%H:%M").time()
            end_time = datetime.datetime.strptime(data['end_time'], "%H:%M").time()

            validation_errors = validate_entry({
                "course_id": int(data['course_id']),
                "subject_id": int(data['subject_id']),
                "teacher_id": int(data['teacher_id']),
                "room_id": int(data['room_id']),
                "day": data['day'],
                "start_time": start_time,
                "end_time": end_time,
                "student_group": data['student_group']
            })

            if validation_errors:
                for error in validation_errors:
                    flash(f"❌ {error}", "danger")
                return redirect(url_for('timetable.add_entry'))

            entry = Timetable(
                course_id=data['course_id'],
                subject_id=data['subject_id'],
                teacher_id=data['teacher_id'],
                room_id=data['room_id'],
                day_of_week=data['day'],
                start_time=start_time,
                end_time=end_time,
                student_group=data['student_group']
            )
            db.session.add(entry)
            db.session.commit()
            flash("✅ Timetable entry added successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Failed to add entry: {e}", "danger")
        return redirect(url_for('timetable.view_timetable'))

    return render_template(
        'timetable/timetable_form.html',
        teachers=Teacher.query.all(),
        subjects=Subject.query.all(),
        rooms=Room.query.all(),
        courses=Course.query.all()
    )

# ------------------ Auto-Generate Timetable ------------------
from services.generate import generate_random_schedule

@timetable_bp.route('/generate')
@login_required
def generate_timetable():
    if current_user.role != 'admin':
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('home'))

    count = generate_random_schedule()
    flash(f"✅ Successfully generated {count} entries without conflicts.", "success")
    return redirect(url_for('timetable.view_timetable'))

# ------------------ Export Timetable as Excel ------------------
@timetable_bp.route('/export/excel')
@login_required
def export_excel():
    if current_user.role != 'admin':
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('home'))

    entries = Timetable.query.all()
    data = []
    for entry in entries:
        data.append({
            "Day": entry.day_of_week,
            "Start Time": entry.start_time.strftime('%H:%M'),
            "End Time": entry.end_time.strftime('%H:%M'),
            "Course": entry.course.name,
            "Subject": entry.subject.name,
            "Teacher": entry.teacher.name,
            "Room": entry.room.name,
            "Student Group": ', '.join(entry.get_students())
        })
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Timetable')
    output.seek(0)
    return send_file(output, download_name="Timetable.xlsx", as_attachment=True)

# ------------------ Export Timetable as PDF ------------------
@timetable_bp.route('/export/pdf')
@login_required
def export_pdf():
    if current_user.role != 'admin':
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('home'))

    entries = Timetable.query.all()
    html = render_template("timetable/timetable_pdf.html", timetable=entries)
    pdf = BytesIO()
    HTML(string=html).write_pdf(pdf)
    pdf.seek(0)
    return send_file(pdf, download_name="Timetable.pdf", as_attachment=True)
