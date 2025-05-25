from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()  # L’unique instance utilisée par tout le projet

class Appel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200))
    description = db.Column(db.Text)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    lien_formulaire = db.Column(db.String(200), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # clé étrangère
    criteres = db.relationship('Critere', backref='appel', lazy=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    entreprise = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255))
    appels = db.relationship('Appel', backref='user', lazy=True)  # relation inverse


class Critere(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    appel_id = db.Column(db.Integer, db.ForeignKey('appel.id'))

class Candidat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    date_naissance = db.Column(db.Date)
    pays = db.Column(db.String(100))
    experience = db.Column(db.Float)
    motivation = db.Column(db.Text)
    linkedin = db.Column(db.String(200))
    fichier_cv = db.Column(db.String(200))
    appel_id = db.Column(db.Integer, db.ForeignKey('appel.id'))
    score = db.Column(db.Float)
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)
