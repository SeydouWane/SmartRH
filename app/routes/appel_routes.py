
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import datetime
from datetime import date
import re
from app.models import db, Appel, Critere, Candidature

appel_bp = Blueprint('appel', __name__)

@appel_bp.route('/dashboard')
@login_required
def appel_dashboard():
    return redirect(url_for('appel.appel_home'))

@appel_bp.route('/appel_home')
@login_required
def appel_home():
    """Affiche le tableau de bord avec les statistiques dynamiques."""
    appels = Appel.query.filter_by(user_id=current_user.id).all()
    
    appels_en_cours = 0
    appels_termines = 0
    candidatures_recues = 0
    today = date.today()

    for appel in appels:
        candidatures_recues += Candidature.query.filter_by(appel_id=appel.id).count()

        if appel.date_fin >= today:
            appels_en_cours += 1
        else:
            appels_termines += 1

    return render_template(
        'appel_dashboard.html',
        appels=appels,
        appels_en_cours=appels_en_cours,
        candidatures_recues=candidatures_recues,
        appels_termines=appels_termines
    )

@appel_bp.route('/create', methods=['GET', 'POST'])
@login_required
def creer_appel():
    """Permet de créer un nouvel appel à candidature."""
    if request.method == 'POST':
        titre = request.form.get('titre')
        date_debut_str = request.form.get('date_debut')
        date_fin_str = request.form.get('date_fin')
        description = request.form.get('description')
        intitules = request.form.getlist('intitule[]')
        scores = request.form.getlist('score[]')

        if not all([titre, date_debut_str, date_fin_str]):
            flash(" Veuillez remplir tous les champs obligatoires.", "danger")
            return redirect(url_for('appel.creer_appel'))

        if not description.strip():
            description = "Aucune description fournie."
        
        try:
            date_debut = datetime.datetime.strptime(date_debut_str, '%Y-%m-%d').date()
            date_fin = datetime.datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            flash(" Format de date invalide.", "danger")
            return redirect(url_for('appel.creer_appel'))

        if date_fin < date_debut:
            flash(" La date de fin ne peut pas être antérieure à la date de début.", "danger")
            return redirect(url_for('appel.creer_appel'))
        
        nom_sans_espace = re.sub(r'[^a-z0-9]', '', titre.replace(" ", "").lower())
        date_str = date_debut.strftime('%d%m%Y')
        lien_slug = f"{nom_sans_espace}{date_str}"

        try:
            nouvel_appel = Appel(
                titre=titre,
                description=description,
                date_debut=date_debut,
                date_fin=date_fin,
                lien_formulaire=lien_slug,
                user_id=current_user.id
            )
            db.session.add(nouvel_appel)
            db.session.flush()

            for i in range(len(intitules)):
                intitule = intitules[i].strip()
                if not intitule:
                    continue
                try:
                    score = int(scores[i]) if scores[i] else 1
                except (ValueError, IndexError):
                    score = 1
                critere = Critere(intitule=intitule, score=score, appel_id=nouvel_appel.id)
                db.session.add(critere)

            db.session.commit()
            flash(f" Appel créé avec succès.", "success")
            return redirect(url_for('appel.appel_home'))
        except Exception as e:
            db.session.rollback()
            flash(" Une erreur s'est produite lors de la création de l'appel. Veuillez réessayer.", "danger")
            return redirect(url_for('appel.creer_appel'))

    return render_template('appel_create_form.html')

@appel_bp.route('/appel/<int:appel_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appel(appel_id):
    """Permet de modifier un appel existant."""
    appel = Appel.query.get_or_404(appel_id)
    if appel.user_id != current_user.id:
        flash(" Vous n'êtes pas autorisé à modifier cet appel.", "danger")
        return redirect(url_for('appel.appel_home'))
        
    if request.method == 'POST':
        appel.titre = request.form['titre']
        appel.description = request.form['description']
        appel.date_debut = request.form['date_debut']
        appel.date_fin = request.form['date_fin']
        db.session.commit()
        flash(' Appel mis à jour avec succès.', 'success')
        return redirect(url_for('appel.appel_home')) 

    return render_template('edit_appel.html', appel=appel)

@appel_bp.route('/appel/<int:appel_id>/delete', methods=['POST'])
@login_required
def delete_appel(appel_id):
    """Permet de supprimer un appel existant."""
    appel = Appel.query.get_or_404(appel_id)
    if appel.user_id != current_user.id:
        flash(" Vous n'êtes pas autorisé à supprimer cet appel.", "danger")
        return redirect(url_for('appel.appel_home'))
        
    db.session.delete(appel)
    db.session.commit()
    flash(" Appel supprimé avec succès.", "success")
    return redirect(url_for('appel.appel_home'))


