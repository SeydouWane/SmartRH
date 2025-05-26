from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import uuid
import datetime
import re

from app.models import db, Appel, Critere, User, Candidature, Candidat

appel_bp = Blueprint('appel', __name__)

@appel_bp.route('/appel/create', methods=['GET', 'POST'])
@login_required
def creer_appel():
    if request.method == 'POST':
        titre = request.form['titre']
        date_debut = request.form['date_debut']
        date_fin = request.form['date_fin']
        description = request.form['description']
        criteres_texte = request.form['criteres']

        # Génération automatique du lien personnalisé
        nom_sans_espace = titre.replace(" ", "").lower()
        date_str = datetime.datetime.strptime(date_debut, '%Y-%m-%d').strftime('%d%m%Y')
        lien_formulaire = f"/formulaire/{nom_sans_espace}{date_str}"

        # Créer l'appel
        from flask_login import current_user

        nouvel_appel = Appel(
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            lien_formulaire=lien_formulaire,
            user_id=current_user.id  # <- associer au recruteur connecté
        )


        db.session.add(nouvel_appel)
        db.session.commit()

        # Ajouter les critères
        for crit in criteres_texte.split(','):
            db.session.add(Critere(nom=crit.strip(), appel_id=nouvel_appel.id))

        db.session.commit()
        flash(f"Appel créé avec succès. Lien : {lien_formulaire}", "success")
        return redirect(url_for('appel.appel_home'))

    return render_template('appel_create_form.html')

@appel_bp.route('/dashboard')
@login_required
def appel_home():
    appels = Appel.query.filter_by(user_id=current_user.id).all()  
    return render_template('appel_dashboard.html', appels=appels)


from flask import render_template, redirect, url_for, request, flash
from app.models import Appel, Critere, db

#  Voir un appel
@appel_bp.route('/appel/<int:appel_id>')
def view_appel(appel_id):
    appel = Appel.query.get_or_404(appel_id)
    return render_template('view_appel.html', appel=appel)

#  Modifier un appel
@appel_bp.route('/appel/<int:appel_id>/edit', methods=['GET', 'POST'])
def edit_appel(appel_id):
    appel = Appel.query.get_or_404(appel_id)

    if request.method == 'POST':
        appel.titre = request.form['titre']
        appel.description = request.form['description']
        appel.date_debut = request.form['date_debut']
        appel.date_fin = request.form['date_fin']
        db.session.commit()
        flash("Appel mis à jour avec succès ✅", "success")
        return redirect(url_for('auth.dashboard'))

    return render_template('edit_appel.html', appel=appel)

#  Supprimer un appel
@appel_bp.route('/appel/<int:appel_id>/delete')
def delete_appel(appel_id):
    appel = Appel.query.get_or_404(appel_id)
    db.session.delete(appel)
    db.session.commit()
    flash("Appel supprimé avec succès 🗑️", "info")
    return redirect(url_for('auth.dashboard'))
