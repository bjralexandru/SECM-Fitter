from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db

# Write-ups for the experiments 
# TODO: Not implemented yet. Will do.

# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     data = db.Column(db.String(10000))
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    

class User(db.Model, UserMixin):
    #the db schema for the users signed up for the notes app
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True) # Cannot sign up with the same email twice
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    data = db.relationship('Data')

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    rT = db.Column(db.Float, nullable=False)
    RG = db.Column(db.Float, nullable=False)
    iT_inf = db.Column(db.Float, nullable=False)
    Kappa = db.Column(db.Float, nullable=False)
    Chi2 = db.Column(db.Float, nullable=False) 
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    