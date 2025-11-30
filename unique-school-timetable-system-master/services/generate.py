import random
import datetime
from app import db
from models.timetable import Timetable
from models.teacher import Teacher
from models.subject import Subject
from models.room import Room
from collections import defaultdict

# Days and Time slots
DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
TIME_SLOTS = [
    ('09:00', '10:00'), ('10:00', '11:00'),
    ('11:00', '12:00'), ('12:00', '01:00'),
    ('02:00', '03:00'), ('03:00', '04:00')
]

# Genetic Algorithm parameters
POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.1

# Ensure Lab subjects are assigned 2-hour consecutive slots
def generate_chromosome(subjects, teachers, rooms):
    chromosome = []
    used_slots = set()  # To track already used time slots
    teacher_hours = defaultdict(int)  # Track teacher's total hours
    subject_hours_assigned = defaultdict(int)  # Track subject hours assigned

    # Assign subjects
    for subj in subjects:
        required_hours = subj.hours_per_week
        assigned_hours = subject_hours_assigned[subj.id]  # Start with hours already assigned
        
        # Ensure all required hours are assigned
        while assigned_hours < required_hours:
            day = random.choice(DAYS)
            start_time, _ = random.choice(TIME_SLOTS)

            # Ensure the time slot isn't already taken
            while (day, start_time) in used_slots:
                start_time, _ = random.choice(TIME_SLOTS)

            # Ensure teacher has capacity and subject is assigned to a teacher who can teach it
            teacher = random.choice([t for t in teachers if t.max_hours_week >= required_hours and subj in t.subjects])
            
            # Room assignment based on the subject type (Lab or Lecture)
            if subj.type == "Lab":
                room = random.choice([r for r in rooms if r.type == 'Lab'])
            else:
                room = random.choice([r for r in rooms if r.type == 'Lecture'])

            gene = {
                'course_id': subj.course_id,
                'subject_id': subj.id,
                'teacher_id': teacher.id,
                'room_id': room.id,
                'day': day,
                'start_time': start_time,
                'end_time': start_time,  # Placeholder, will be updated later
                'student_group': 'A'
            }

            # Update assignments and track assigned hours
            chromosome.append(gene)
            used_slots.add((day, start_time))
            teacher_hours[teacher.id] += 1
            subject_hours_assigned[subj.id] += 1
            assigned_hours += 1

    return chromosome

def fitness(chromosome):
    score = 0
    seen = set()
    teacher_hours = defaultdict(int)
    room_occupancy = defaultdict(int)

    for gene in chromosome:
        key = (gene['day'], gene['start_time'], gene['teacher_id'])
        room_key = (gene['day'], gene['start_time'], gene['room_id'])

        if key in seen:
            score -= 5  # Teacher conflict
        else:
            seen.add(key)

        if room_key in room_occupancy:
            score -= 5  # Room conflict
        else:
            room_occupancy[room_key] = True

        teacher_hours[gene['teacher_id']] += 1

    # Check if any teacher exceeds max hours
    for tid, hours in teacher_hours.items():
        teacher = Teacher.query.get(tid)
        if teacher and hours > teacher.max_hours_week:
            score -= 3  # Exceeded teacher's max hours

    return score

def crossover(parent1, parent2):
    split = len(parent1) // 2
    return parent1[:split] + parent2[split:]

def mutate(chromosome):
    idx = random.randint(0, len(chromosome) - 1)
    gene = chromosome[idx]
    gene['day'] = random.choice(DAYS)
    gene['start_time'], gene['end_time'] = random.choice(TIME_SLOTS)
    return chromosome

def generate_random_schedule():
    subjects = Subject.query.all()
    teachers = Teacher.query.all()
    rooms = Room.query.all()

    # Ensure there is data in subjects, teachers, and rooms
    if not subjects or not teachers or not rooms:
        print("Missing data in subjects, teachers, or rooms.")
        return 0  # No timetable generated if data is missing

    # Clear any existing timetable before generating new one
    Timetable.query.delete()
    db.session.commit()

    population = [generate_chromosome(subjects, teachers, rooms) for _ in range(POPULATION_SIZE)]

    for _ in range(GENERATIONS):
        population.sort(key=fitness, reverse=True)
        new_generation = population[:10]  # Elitism: keep the best 10

        while len(new_generation) < POPULATION_SIZE:
            p1, p2 = random.sample(population[:20], 2)
            child = crossover(p1, p2)
            if random.random() < MUTATION_RATE:
                child = mutate(child)
            new_generation.append(child)

        population = new_generation

    best_schedule = population[0]

    count = 0
    for gene in best_schedule:
        start_time = datetime.datetime.strptime(gene['start_time'], "%H:%M").time()
        end_time = datetime.datetime.strptime(gene['end_time'], "%H:%M").time()

        entry = Timetable(
            course_id=gene['course_id'],
            subject_id=gene['subject_id'],
            teacher_id=gene['teacher_id'],
            room_id=gene['room_id'],
            day_of_week=gene['day'],
            start_time=start_time,
            end_time=end_time,
            student_group=gene['student_group']
        )
        db.session.add(entry)
        count += 1

    db.session.commit()
    return count
