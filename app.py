from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pyodbc
from dotenv import load_dotenv
import os
load_dotenv()
app = Flask(__name__)
app.secret_key = "your_secure_secret_key"
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Admin and User models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class User1(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('action') == 'login':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role'].lower()  # Convert to lowercase to avoid case-sensitivity

            if role == 'admin':
                admin = Admin.query.filter_by(username=username, password=password).first()
                if admin:
                    session['admin_logged_in'] = True
                    return redirect(url_for('admin_dashboard'))
                else:
                    return "Invalid admin credentials. Please try again."
            elif role == 'user':
                user = User1.query.filter_by(username=username, password=password).first()
                if user:
                    session['user_logged_in'] = True
                    return redirect(url_for('user_dashboard'))
                else:
                    return "Invalid user credentials. Please try again."

        elif request.form.get('action') == 'signup':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role'].lower()  # Convert to lowercase

            if role == 'admin':
                new_admin = Admin(username=username, password=password)
                try:
                    db.session.add(new_admin)
                    db.session.commit()
                    return "Admin account created successfully!"
                except Exception as e:
                    return f"Error creating admin account: {str(e)}"
            elif role == 'user':
                new_user = User1(username=username, password=password)
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    return "User account created successfully!"
                except Exception as e:
                    return f"Error creating user account: {str(e)}"

    return render_template('index.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_logged_in' in session:
        return "Welcome to Admin Dashboard!"
    else:
        return redirect(url_for('index'))

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_logged_in' in session:
        return "Welcome to User Dashboard!"
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
