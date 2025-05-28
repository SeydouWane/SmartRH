from flask_login import UserMixin
from datetime import datetime
from app import db  # Reprend bien l'instance créée dans __init__.py

#  Utilisateur (Recruteur)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    entreprise = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255))

    # 🔗 Relation : un utilisateur peut créer plusieurs appels
    appels = db.relationship('Appel', backref='user', lazy=True)

#  Appel à candidature
class Appel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200))
    description = db.Column(db.Text)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    criteres = db.relationship('Critere', backref='appel', lazy=True)
    candidatures = db.relationship('Candidature', backref='appel', lazy=True)

    lien_formulaire = db.Column(db.String(200), unique=True)

    # Lien vers le recruteur
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Critères associés à l'appel
    criteres = db.relationship('Critere', backref='appel', lazy=True)

    # Candidatures reçues
    candidatures = db.relationship('Candidature', backref='appel', lazy=True)

    # Candidats classés (si tu les utilises séparément de Candidature)
    candidats = db.relationship('Candidat', backref='appel', lazy=True)



#  Candidat (version enrichie avec score)
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
    score = db.Column(db.Float)
    date_soumission = db.Column(db.DateTime, default=datetime.utcnow)

    appel_id = db.Column(db.Integer, db.ForeignKey('appel.id'))


class Candidature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    email = db.Column(db.String(120))
    telephone = db.Column(db.String(20))
    cv_filename = db.Column(db.String(200))
    lettre_motivation = db.Column(db.Text)
    experience = db.Column(db.Integer)
    date_soumission = db.Column(db.DateTime, default=db.func.now())
    appel_id = db.Column(db.Integer, db.ForeignKey('appel.id'))

class Critere(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intitule = db.Column(db.String(100))
    appel_id = db.Column(db.Integer, db.ForeignKey('appel.id'))
