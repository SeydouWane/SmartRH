from flask import Blueprint, render_template
from app.models import Appel, Candidature
import os
import re

classement_bp = Blueprint('classement', __name__)

# Fonction NLP simplifiée pour détecter les critères dans un CV
def extraire_criteres_du_cv(cv_path, criteres_recherches):
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(cv_path)
        texte = ''
        for page in reader.pages:
            texte += page.extract_text() or ''
        texte = texte.lower()
        return sum(1 for critere in criteres_recherches if critere.lower() in texte)
    except Exception as e:
        print(f"Erreur lecture CV {cv_path} : {e}")
        return 0

@classement_bp.route('/appel/<int:appel_id>/candidatures')
def classement_candidatures(appel_id):
    appel = Appel.query.get_or_404(appel_id)
    candidatures = appel.candidatures

    # Liste des critères de l’appel
    criteres = [crit.intitule for crit in appel.criteres]
    uploads_dir = os.path.join('app', 'static', 'uploads')

    resultats = []

    for c in candidatures:
        # Chemin du fichier CV
        cv_path = os.path.join(uploads_dir, c.cv_filename)
        score_criteres = extraire_criteres_du_cv(cv_path, criteres)
        score_experience = int(c.experience or 0)
        score_total = score_criteres + score_experience

        resultats.append({
            'candidat': c,
            'score_criteres': score_criteres,
            'score_experience': score_experience,
            'score': score_total
        })

    # Tri par score décroissant
    resultats = sorted(resultats, key=lambda x: x['score'], reverse=True)

    return render_template('candidatures_par_appel.html', appel=appel, resultats=resultats)
