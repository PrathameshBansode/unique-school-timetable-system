from flask import Blueprint, render_template, request, send_file
from models.room import Room
from models.timetable import Timetable
import pandas as pd
from io import BytesIO

room_timetable_bp = Blueprint('room_timetable', __name__)

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
TIME_SLOTS = [
    ('09:00', '10:00'),
    ('10:00', '11:00'),
    ('11:00', '12:00'),
    ('12:00', '13:00'),
    ('13:00', '14:00'),
    ('14:00', '15:00'),
    ('15:00', '16:00'),
    ('16:00', '17:00'),
]

@room_timetable_bp.route('/manage/room_timetable', methods=['GET', 'POST'])
def room_timetable():
    rooms = Room.query.all()
    timetable = []
    selected_room = None
    grid = None

    if request.method == 'POST':
        room_id = request.form.get('room_id')
        selected_room = Room.query.get(room_id)

        if selected_room:
            raw_entries = Timetable.query.filter_by(room_id=room_id).order_by(
                Timetable.day_of_week, Timetable.start_time
            ).all()

            # Filter lab/theory based on room type
            timetable = []
            for entry in raw_entries:
                is_lab = 'lab' in entry.subject.name.lower()
                if (is_lab and selected_room.type == 'Lab') or (not is_lab and selected_room.type != 'Lab'):
                    timetable.append(entry)

            # Grid structure: TIME_SLOTS × DAYS
            grid = {slot: {day: None for day in DAYS} for slot in TIME_SLOTS}
            for entry in timetable:
                slot = (entry.start_time.strftime('%H:%M'), entry.end_time.strftime('%H:%M'))
                cell = f"{entry.subject.name}<br><small>{entry.teacher.name}<br>{entry.course.name}</small>"
                if slot in grid and entry.day_of_week in grid[slot]:
                    grid[slot][entry.day_of_week] = cell

    return render_template('room_timetable.html', rooms=rooms, selected_room=selected_room, grid=grid,
                           time_slots=TIME_SLOTS, days=DAYS)

@room_timetable_bp.route('/manage/room_timetable/export/<int:room_id>', methods=['GET'])
def export_room_timetable(room_id):
    selected_room = Room.query.get(room_id)
    raw_entries = Timetable.query.filter_by(room_id=room_id).order_by(
        Timetable.day_of_week, Timetable.start_time
    ).all()

    timetable = []
    for entry in raw_entries:
        is_lab = 'lab' in entry.subject.name.lower()
        if (is_lab and selected_room.type == 'Lab') or (not is_lab and selected_room.type != 'Lab'):
            timetable.append(entry)

    # Build exportable grid
    grid = {slot: {day: '' for day in DAYS} for slot in TIME_SLOTS}
    for entry in timetable:
        slot = (entry.start_time.strftime('%H:%M'), entry.end_time.strftime('%H:%M'))
        cell = f"{entry.subject.name}\n{entry.teacher.name}\n{entry.course.name}"
        if slot in grid and entry.day_of_week in grid[slot]:
            grid[slot][entry.day_of_week] = cell

    # Build DataFrame
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
    return send_file(output, download_name=f"{selected_room.name}_Timetable.xlsx", as_attachment=True)
