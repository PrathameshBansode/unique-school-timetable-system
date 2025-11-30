from flask import Blueprint, render_template, request, send_file
from models.teacher import Teacher
from models.timetable import Timetable
import pandas as pd
from io import BytesIO

teacher_timetable_bp = Blueprint('teacher_timetable', __name__)

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
TIME_SLOTS = [
    ('09:00', '10:00'), ('10:00', '11:00'),
    ('11:00', '12:00'), ('12:00', '13:00'),
    ('13:00', '14:00'), ('14:00', '15:00'),
    ('15:00', '16:00'), ('16:00', '17:00'),
]

@teacher_timetable_bp.route('/manage/teacher_timetable', methods=['GET', 'POST'])
def teacher_timetable():
    teachers = Teacher.query.all()
    timetable = []
    selected_teacher = None
    grid = None

    if request.method == 'POST':
        teacher_id = request.form.get('teacher_id')
        selected_teacher = Teacher.query.get(teacher_id)

        if selected_teacher:
            timetable = Timetable.query.filter_by(teacher_id=teacher_id).order_by(
                Timetable.day_of_week, Timetable.start_time
            ).all()

            # Grid setup
            grid = {slot: {day: None for day in DAYS} for slot in TIME_SLOTS}
            for entry in timetable:
                slot = (entry.start_time.strftime('%H:%M'), entry.end_time.strftime('%H:%M'))
                cell = f"{entry.subject.name}<br><small>{entry.room.name}<br>{entry.course.name}</small>"
                if slot in grid and entry.day_of_week in grid[slot]:
                    grid[slot][entry.day_of_week] = cell

    return render_template('teacher_timetable.html', teachers=teachers, selected_teacher=selected_teacher,
                           grid=grid, time_slots=TIME_SLOTS, days=DAYS)

@teacher_timetable_bp.route('/manage/teacher_timetable/export/<int:teacher_id>', methods=['GET'])
def export_teacher_timetable(teacher_id):
    selected_teacher = Teacher.query.get(teacher_id)
    timetable = Timetable.query.filter_by(teacher_id=teacher_id).order_by(
        Timetable.day_of_week, Timetable.start_time
    ).all()

    grid = {slot: {day: '' for day in DAYS} for slot in TIME_SLOTS}
    for entry in timetable:
        slot = (entry.start_time.strftime('%H:%M'), entry.end_time.strftime('%H:%M'))
        cell = f"{entry.subject.name}\n{entry.room.name}\n{entry.course.name}"
        if slot in grid and entry.day_of_week in grid[slot]:
            grid[slot][entry.day_of_week] = cell

    data = []
    for start, end in TIME_SLOTS:
        row = {'Time Slot': f"{start} - {end}"}
        for day in DAYS:
            row[day] = grid[(start, end)][day]
        data.append(row)

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Timetable')

    output.seek(0)
    return send_file(output, download_name=f"{selected_teacher.name}_Timetable.xlsx", as_attachment=True)
