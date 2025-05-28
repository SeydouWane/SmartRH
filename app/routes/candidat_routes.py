from flask import Blueprint, render_template, request, redirect, flash, url_for
from app.models import db, Appel, Candidat
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from app.models import Candidature, Candidat, Appel, db
from app.models import db, Appel, Critere, User, Candidature, Candidat

candidat_bp = Blueprint('candidat', __name__)

@candidat_bp.route('/formulaire/<string:lien>')
def afficher_formulaire(lien):
    appel = Appel.query.filter_by(lien_formulaire=f'/formulaire/{lien}').first_or_404()
    return render_template('formulaire_candidat.html', appel=appel)


UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')

@candidat_bp.route('/formulaire/<string:lien>', methods=['POST'])
def soumettre_formulaire(lien):
    appel = Appel.query.filter_by(lien_formulaire=f'/formulaire/{lien}').first_or_404()

    try:
        # 1. Récupération des champs du formulaire
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form.get('telephone', '')
        lettre_motivation = request.form.get('motivation', '')
        experience = request.form.get('experience', type=float)

        # 2. Gestion du fichier CV
        fichier = request.files.get('cv')
        if not fichier or fichier.filename == '':
            flash("⚠️ Veuillez fournir un fichier CV valide.", "danger")
            return redirect(request.url)

        filename = secure_filename(fichier.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        chemin_complet = os.path.join(UPLOAD_FOLDER, filename)
        fichier.save(chemin_complet)

        # 3. Création de la candidature
        candidature = Candidature(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            lettre_motivation=lettre_motivation,
            cv_filename=filename,
            appel_id=appel.id,
            experience=experience
        )

        db.session.add(candidature)
        db.session.commit()

        flash("✅ Votre candidature a bien été enregistrée.", "success")
        return redirect(request.url)

    except Exception as e:
        flash(f"❌ Erreur lors de la soumission : {str(e)}", "danger")
        return redirect(request.url)


@candidat_bp.route('/appel/<int:appel_id>/candidatures') 
def list_candidatures(appel_id):
    appel = Appel.query.get_or_404(appel_id)
    candidatures = Candidature.query.filter_by(appel_id=appel_id).all()
    criteres = [c.intitule.lower() for c in appel.criteres]  # Critères de l’appel

    resultats = []

    for candidat in candidatures:
        score_criteres = 0

        # Chemin complet du CV
        chemin_cv = os.path.join('app', 'static', 'uploads', candidat.cv_filename)

        # Lire le texte du CV
        texte_cv = ""
        if os.path.exists(chemin_cv):
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(chemin_cv)
                texte_cv = " ".join([page.get_text() for page in doc])
            except Exception as e:
                print(f"Erreur lecture CV : {e}")
        texte_cv = texte_cv.lower()

        # Score basé sur les critères
        for critere in criteres:
            if critere in texte_cv:
                score_criteres += 1

        # ✅ Score basé sur l'expérience déclarée
        score_experience = candidat.experience or 0  # Directement depuis le champ DB

        # Score final
        score_total = score_criteres + score_experience

        resultats.append({
            'candidat': candidat,
            'score_criteres': score_criteres,
            'score_experience': score_experience,
            'score': score_total
        })

    # Trier les candidats par score décroissant
    resultats = sorted(resultats, key=lambda x: x['score'], reverse=True)

    return render_template("candidatures_par_appel.html", appel=appel, resultats=resultats)
