from models.timetable import Timetable
from models.teacher import Teacher
from models.room import Room
from datetime import time

def validate_entry(entry):
    errors = []

    day = entry["day"]
    start = entry["start_time"]
    end = entry["end_time"]
    teacher_id = int(entry["teacher_id"])
    room_id = int(entry["room_id"])

    # --------- Constraint 1: Start < End ---------
    if start >= end:
        errors.append("Start time must be before end time.")

    # --------- Constraint 2: Room Conflict ---------
    existing_room_entries = Timetable.query.filter_by(day_of_week=day, room_id=room_id).all()
    for e in existing_room_entries:
        if time_overlap(start, end, e.start_time, e.end_time):
            errors.append(f"Room is already booked on {day} from {e.start_time} to {e.end_time}.")
            break

    # --------- Constraint 3: Teacher Conflict ---------
    existing_teacher_entries = Timetable.query.filter_by(day_of_week=day, teacher_id=teacher_id).all()
    for e in existing_teacher_entries:
        if time_overlap(start, end, e.start_time, e.end_time):
            errors.append(f"Teacher has a clash on {day} from {e.start_time} to {e.end_time}.")
            break

    # --------- Constraint 4: Teacher Weekly Hours ---------
    teacher = Teacher.query.get(teacher_id)
    weekly_hours = sum(
        (datetime_to_minutes(e.end_time) - datetime_to_minutes(e.start_time)) / 60
        for e in Timetable.query.filter_by(teacher_id=teacher_id).all()
    )
    current_duration = (datetime_to_minutes(end) - datetime_to_minutes(start)) / 60
    if teacher and (weekly_hours + current_duration > teacher.max_hours_week):
        errors.append(f"Teacher would exceed weekly hours limit of {teacher.max_hours_week}.")

    # --------- Constraint 5: Room Capacity (if needed) ---------
    # You can implement it if student_group is linked to a count.

    return errors

# ------------------ Utility Functions ------------------

def time_overlap(start1, end1, start2, end2):
    """Returns True if time ranges [start1, end1] and [start2, end2] overlap"""
    return max(start1, start2) < min(end1, end2)

def datetime_to_minutes(t):
    """Converts a time object to minutes since midnight"""
    return t.hour * 60 + t.minute
