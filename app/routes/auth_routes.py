from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app.models import db, Appel, Critere, User, Candidature, Candidat

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        entreprise = request.form['entreprise']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.", "danger")
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        user = User(nom=nom, prenom=prenom, entreprise=entreprise, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Inscription réussie ! Connectez-vous maintenant.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Connexion réussie.", "success")
            return redirect(url_for('appel.appel_home'))
        else:
            flash("Email ou mot de passe incorrect.", "danger")

    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])  # ← C'est ça qui manque souvent
@login_required
def logout():
    logout_user()
    flash('Déconnexion réussie.')
    return redirect(url_for('auth.login'))

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

from flask_login import current_user, login_required
from app.models import Appel

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    appels = Appel.query.filter_by(user_id=current_user.id).all()
    return render_template('appel_dashboard.html', appels=appels)
