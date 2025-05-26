from flask_login import UserMixin
from datetime import datetime
from app import db  # Reprend l’instance déjà créée dans __init__.py

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    entreprise = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255))
    appels = db.relationship('Appel', backref='user', lazy=True)

class Appel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200))
    description = db.Column(db.Text)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    lien_formulaire = db.Column(db.String(200), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    criteres = db.relationship('Critere', backref='appel', lazy=True)
    candidatures = db.relationship('Candidature', backref='appel', lazy=True)

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

class Candidature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telephone = db.Column(db.String(20), nullable=True)
    cv_filename = db.Column(db.String(200), nullable=True)
    lettre_motivation = db.Column(db.Text, nullable=True)
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)
    appel_id = db.Column(db.Integer, db.ForeignKey('appel.id'), nullable=False)
