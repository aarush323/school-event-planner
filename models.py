from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)

class Club(db.Model):
    __tablename__ = 'club'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    

   


class UserClub(db.Model):
    __tablename__ = 'user_clubs'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), primary_key=True)

class EventAttendee(db.Model):
    __tablename__ = 'event_attendees'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    interested=db.Column(db.Integer, default = 0)

class EventRating(db.Model):
    __tablename__ = 'event_ratings'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
