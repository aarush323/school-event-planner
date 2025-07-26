from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Club, Event, EventAttendee,EventRating,UserClub
import bcrypt
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password'].encode('utf-8')
        role=request.form['role']
        teacher_code = request.form.get('teacher_code', '')

        if role == 'teacher' and teacher_code != 'admin123':
            flash("Invalid teacher code.")
            return redirect('/register')

        if User.query.filter_by(email=email).first():
            flash("User already exists.")
            return redirect('/register')
        
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        if User.query.filter_by(email=email).first():
            flash("User already exists.")
            return redirect('/register')

        new_user = User(email=email, password=hashed, role=role)

        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully!")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        clubs = Club.query.all() 
        return render_template('login.html', clubs=clubs)

    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password'].encode('utf-8')
        

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.checkpw(password, user.password):
            session['user_id'] = user.id
            flash("Login successful!")
            return redirect('/dashboard')
        else:
            flash("Invalid credentials.")
            return redirect('/login')

@app.route('/add-event', methods=['GET', 'POST'])
def event_add():
    if 'user_id' not in session:
        flash("Please log in to create an event.")
        return redirect('/login')

    if request.method == 'GET':
        clubs = Club.query.all()
      
        return render_template('add-event.html', clubs=clubs)

    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        time = request.form['time']
        club_id = request.form['club_id']

        club = Club.query.get(club_id)
        if not club:
            flash("Invalid club selected.")
            return redirect('/add-event')

        new_event = Event(title=title, date=date, time=time, club_id=club_id)
        db.session.add(new_event)
        db.session.commit()

        flash("Event created successfully!")
        return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    events = Event.query.all()
    clubs = {club.id: club.name for club in Club.query.all()}
    interested_counts = {}
    for event in events:
        count = EventAttendee.query.filter_by(event_id=event.id, interested=True).count()
        interested_counts[event.id] = count
    return render_template(
        'dashboard.html',
        user=user,
        events=events,
        clubs=clubs,
        interested_counts=interested_counts
    )


@app.route('/setup-clubs')
def setup_clubs():
    sample_clubs = ['ACM Club', 'Art Circle', 'MUN', 'TEDx']
    for name in sample_clubs:
        if not Club.query.filter_by(name=name).first(): 
            db.session.add(Club(name=name))
    db.session.commit()
    return "Sample clubs added successfully!"

@app.route('/setup-all')
def setup_all():
    club_names = ['ACM Club', 'Art Circle', 'MUN', 'TEDx']
    for name in club_names:
        if not Club.query.filter_by(name=name).first():
            db.session.add(Club(name=name))

    if not User.query.filter_by(email='test@example.com').first():
        hashed_pw = bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt())
        db.session.add(User(email='test@example.com', password=hashed_pw))

    db.session.commit()
    
    sample_club = Club.query.first()
    if sample_club and not Event.query.filter_by(title='Sample Event').first():
        db.session.add(Event(
            title='Sample Event',
            date='2025-07-31',
            time='18:00',
            club_id=sample_club.id
        ))
        db.session.commit()

    return "✅ Setup complete: Sample clubs, user, and event added."

@app.route('/event_interaction', methods=['POST'])
def event_interaction():
    interested = request.form['interested'] == "true"  
    user_id = session['user_id']
    event_id = request.form['event_id']

    attendee = EventAttendee.query.filter_by(user_id=user_id, event_id=event_id).first()

    if attendee:
        attendee.interested = interested
    else:
        attendee = EventAttendee(user_id=user_id, event_id=event_id, interested=interested)
        db.session.add(attendee)

    db.session.commit() 

    count = EventAttendee.query.filter_by(event_id=event_id, interested=True).count()

    flash(f"{count} people are interested in this event.")
    return redirect('/dashboard')
    

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out.")
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
