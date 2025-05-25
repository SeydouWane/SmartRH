from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.models import db, Appel, Candidat
import os
from werkzeug.utils import secure_filename
from datetime import datetime

candidat_bp = Blueprint('candidat', __name__)

@candidat_bp.route('/formulaire/<string:lien>')
def afficher_formulaire(lien):
    appel = Appel.query.filter_by(lien_formulaire=f'/formulaire/{lien}').first_or_404()
    return render_template('formulaire_candidat.html', appel=appel)

@candidat_bp.route('/formulaire/<string:lien>', methods=['POST'])
def soumettre_formulaire(lien):
    appel = Appel.query.filter_by(lien_formulaire=f'/formulaire/{lien}').first_or_404()

    nom = request.form['nom']
    prenom = request.form['prenom']
    date_naissance = request.form['date_naissance']
    pays = request.form['pays']
    experience = request.form['experience']
    motivation = request.form['motivation']
    linkedin = request.form['linkedin']
    
    fichier = request.files['cv']
    filename = secure_filename(fichier.filename)
    path = os.path.join('app/uploads', filename)
    fichier.save(path)

    candidat = Candidat(
        nom=nom,
        prenom=prenom,
        date_naissance=date_naissance,
        pays=pays,
        experience=experience,
        motivation=motivation,
        linkedin=linkedin,
        fichier_cv=filename,
        appel_id=appel.id
    )

    db.session.add(candidat)
    db.session.commit()
    flash(" Votre candidature a été enregistrée avec succès !", "success")
    return redirect(request.url)
