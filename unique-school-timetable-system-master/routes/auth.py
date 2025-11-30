from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.user import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def landing():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # Validate credentials
        if user and user.check_password(password):  # Use the check_password method
            login_user(user)
            flash(f"Welcome, {user.name}!", "success")
            return redirect(url_for('dashboard.home'))  # Assuming 'dashboard.home' is the landing page after login
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
