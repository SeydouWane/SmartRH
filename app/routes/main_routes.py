# app/routes/main_routes.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('appel.appel_home'))
    return render_template('accueil.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('appel.appel_home'))

@main_bp.route('/fonctions')
def fonctions():
    """Affiche la page des fonctionnalités."""
    return render_template('fonctions.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route("/profil")
@login_required
def profil():
    """Affiche la page de profil de l'utilisateur."""
    # Vous pouvez passer des données de l'utilisateur au template
    return render_template('profil.html', user=current_user)

@main_bp.route("/parametres")
@login_required
def parametres():
    """Affiche la page de paramètres de l'utilisateur."""
    # Vous pouvez passer des données spécifiques aux paramètres
    return render_template('parametres.html', user=current_user)