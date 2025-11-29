from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.models import db, User
from datetime import datetime

auth = Blueprint('auth', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin@example.com" and password == "admin123":
            admin_user = User.query.filter_by(username="admin@example.com").first()
            if admin_user:
                login_user(admin_user)
                return redirect(url_for('admin.dashboard'))
            else:
                flash("Admin account does not exist in the database. Please contact support.")
                return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))

        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d')

        if username == "admin@example.com":
            flash("You cannot register as an admin.")
            return redirect(url_for('auth.register'))

        user = User.query.filter_by(username=username).first()
        if user:
            flash('User already exists.')
            return redirect(url_for('auth.register'))

        new_user = User(
            username=username,
            full_name=full_name,
            qualification=qualification,
            dob=dob,
            is_admin=False  
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
