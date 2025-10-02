# app/models.py
from flask_login import UserMixin
from datetime import datetime
from app import db  # Reprend bien l'instance créée dans __init__.py

#  Utilisateur (Recruteur)
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    entreprise = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # Relation avec la table Appel 
    appels = db.relationship('Appel', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"

#  Appel à candidature
class Appel(db.Model):
    __tablename__ = 'appels'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date_debut = db.Column(db.Date, default=datetime.utcnow)
    date_fin = db.Column(db.Date, nullable=False)
    lien_formulaire = db.Column(db.String(200), unique=True, nullable=False)
    # Clé étrangère vers l'utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relations avec les autres modèles
    candidatures = db.relationship('Candidature', backref='appel', lazy=True, cascade='all, delete-orphan')
    criteres = db.relationship('Critere', backref='appel', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Appel {self.titre}>"

#  Candidat (Informations sur la personne)
class Candidat(db.Model):
    __tablename__ = 'candidats'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    linkedin = db.Column(db.String(200))
    cv_filename = db.Column(db.String(200), nullable=False)
    motivation = db.Column(db.Text)
    experience = db.Column(db.Float)
    
    # La relation est définie par le backref dans Candidature pour ne pas dupliquer
    candidatures = db.relationship('Candidature', backref='candidat', lazy=True)

    def __repr__(self):
        return f"<Candidat {self.nom} {self.prenom}>"

# Candidature (Lien entre un Candidat et un Appel, avec les scores)
class Candidature(db.Model):
    __tablename__ = 'candidatures'
    id = db.Column(db.Integer, primary_key=True)
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)

    # Clés étrangères vers Appel et Candidat
    appel_id = db.Column(db.Integer, db.ForeignKey('appels.id'), nullable=False)
    candidat_id = db.Column(db.Integer, db.ForeignKey('candidats.id'), nullable=False)
    
    # Champs pour le scoring
    score = db.Column(db.Float)
    score_criteres = db.Column(db.Float)
    score_experience = db.Column(db.Float)
    
    def __repr__(self):
        return f"<Candidature ID:{self.id} | Score:{self.score}>"

#  Critère (Compétence liée à un appel)
class Critere(db.Model):
    __tablename__ = 'criteres'
    id = db.Column(db.Integer, primary_key=True)
    intitule = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Integer, default=1)
    appel_id = db.Column(db.Integer, db.ForeignKey('appels.id'), nullable=False)

    def __repr__(self):
        return f"<Critere {self.intitule}>"