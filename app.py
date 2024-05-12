from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] ="mssql+pyodbc://user:12345678@103.31.104.114:1433/Voting?driver=ODBC+Driver+17+for+SQL+Server"
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
                    # Set the election ID in session upon login
                    set_election_id()
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

def set_election_id():
    # Retrieve the latest election from the database
    latest_election = Elections.query.order_by(Elections.start_date.desc()).first()
    if latest_election:
        session['election_id'] = latest_election.id
    else:
        # Handle the case where there are no elections in the database
        session['election_id'] = None

class Elections(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    election_name = db.Column(db.String(100), nullable=False)

class Candidates(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    candidate_name = db.Column(db.String(100), nullable=False)
    party_affiliation = db.Column(db.String(100))

@app.route('/admin_dashboard')
def admin_dashboard():
    elections = Elections.query.all()
    return render_template('admin_dashboard.html', elections=elections)

@app.route('/create_election', methods=['POST'])
def create_election():
    election_name = request.form['election_name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    new_election = Elections(election_name=election_name, start_date=start_date, end_date=end_date)
    db.session.add(new_election)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    election_id = request.form['election_id']
    candidate_name = request.form['candidate_name']
    party_affiliation = request.form['party_affiliation']
    new_candidate = Candidates(election_id=election_id, candidate_name=candidate_name, party_affiliation=party_affiliation)
    db.session.add(new_candidate)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

class VoteCount(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    vote_count = db.Column(db.Integer, nullable=False, default=0)

@app.route('/user_dashboard')
def user_dashboard():
    # Check if election_id is set in the session
    if 'election_id' not in session:
        return "Please select an election first."
    
    # Get candidates for the selected election
    candidates = Candidates.query.filter_by(election_id=session['election_id']).all()
    
    return render_template('user_dashboard.html', candidates=candidates)

@app.route('/vote', methods=['POST'])
def vote():
    if 'voted' not in session:
        candidate_id = request.form['candidate']
        vote_entry = VoteCount.query.filter_by(candidate_id=candidate_id).first()
        if vote_entry:
            vote_entry.vote_count += 1
        else:
            new_vote_entry = VoteCount(candidate_id=candidate_id, vote_count=1)
            db.session.add(new_vote_entry)
        db.session.commit()
        session['voted'] = True
        return "Vote successful!"
    else:
        return "You have already voted."
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
