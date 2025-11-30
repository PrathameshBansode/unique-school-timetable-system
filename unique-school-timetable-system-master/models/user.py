from flask_login import UserMixin
from sqlalchemy import Enum as PgEnum
from enum import Enum
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class UserRole(Enum):
    ADMIN = 'Admin'
    TEACHER = 'Teacher'
    STUDENT = 'Student'
    STAFF = 'SupportStaff'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(PgEnum(UserRole), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(15))

    def __init__(self, username, password, role, name=None, email=None, phone=None):
        self.username = username
        self.password = generate_password_hash(password)  # Hash the password
        self.role = role
        self.name = name
        self.email = email
        self.phone = phone

    def get_id(self):
        return str(self.id)

    def check_password(self, password):
        return check_password_hash(self.password, password)  # Check the hashed password

    def is_admin(self):
        return self.role == UserRole.ADMIN

    def is_teacher(self):
        return self.role == UserRole.TEACHER

    def is_student(self):
        return self.role == UserRole.STUDENT

    def is_staff(self):
        return self.role == UserRole.STAFF
