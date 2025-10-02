# app/routes/candidat_routes.py

from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, send_file, make_response
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.models import db, Appel, Candidat, Candidature, Critere
from app.services.file_extraction import extract_text_from_file
from app.services.nlp_scoring import calculate_semantic_score
from app.services.experience_parser import calculate_experience_score
from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app
from werkzeug.utils import secure_filename
from app.services.pdf_extraction import extract_text_from_pdf
from app.services.experience_parser import extract_experience_years, calculate_experience_score
from fpdf import FPDF
from flask import send_from_directory
import pandas as pd
from io import BytesIO
from flask import send_file


candidat_bp = Blueprint('candidat', __name__)

# Définition du dossier de téléversement
UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')

@candidat_bp.route('/formulaire/<string:lien>')
def afficher_formulaire(lien):
    """
    Affiche le formulaire de candidature pour un appel donné.
    """
    appel = Appel.query.filter_by(lien_formulaire=lien).first_or_404()
    return render_template('formulaire_candidat.html', appel=appel)

# Définition du dossier de téléversement

@candidat_bp.route('/formulaire/<string:lien>', methods=['POST'])
def soumettre_formulaire(lien):
    """
    Traite la soumission du formulaire de candidature et exécute la logique de scoring.
    """
    appel = Appel.query.filter_by(lien_formulaire=lien).first_or_404()

    try:
        # 1. Récupération des données du formulaire
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form.get('telephone', '')
        lettre_motivation = request.form.get('motivation', '')
        
        annees_experience_str = request.form.get('experience', '0')
        try:
            annees_experience = float(annees_experience_str)
        except (ValueError, TypeError):
            annees_experience = 0.0

        # 2. Gestion et sauvegarde du fichier CV
        cv_file = request.files.get('cv')
        if not cv_file or cv_file.filename == '':
            flash("⚠️ Veuillez fournir un fichier CV valide.", "danger")
            return redirect(request.url)

        # Assurer un nom de fichier unique et sécurisé
        filename = secure_filename(f"{email}_{appel.id}_{cv_file.filename}")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        cv_path = os.path.join(UPLOAD_FOLDER, filename)
        cv_file.save(cv_path)

        # 3. Extraction du texte du CV
        cv_text = extract_text_from_file(cv_path)
        if not cv_text:
            flash("❌ Impossible d'extraire le texte du CV. Le format de fichier est peut-être non supporté ou le fichier est corrompu.", "danger")
            return redirect(request.url)

        # 4. Récupération des critères de l'appel depuis la base de données
        criteres = [{'intitule': c.intitule, 'score': c.score} for c in appel.criteres]

        # 5. Calcul des scores en utilisant les services
        score_criteres, criteres_trouves = calculate_semantic_score(cv_text, criteres)
        score_experience = calculate_experience_score(annees_experience)

        # 6. Calcul du score final pondéré (poids 70% pour les critères, 30% pour l'expérience)
        score_total = (score_criteres * 0.7) + (score_experience * 0.3)

        # 7. Création ou mise à jour du candidat et de la candidature
        # Vérifier si un candidat avec cet email existe déjà
        candidat = Candidat.query.filter_by(email=email).first()
        if not candidat:
            candidat = Candidat(
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone,
                experience=annees_experience,
                motivation=lettre_motivation,
                cv_filename=filename
            )
            db.session.add(candidat)
        else:
            # Si le candidat existe, mettez à jour ses informations
            candidat.nom = nom
            candidat.prenom = prenom
            candidat.telephone = telephone
            candidat.experience = annees_experience
            candidat.motivation = lettre_motivation
            candidat.cv_filename = filename

        # Vérifier si une candidature pour cet appel existe déjà pour ce candidat
        candidature = Candidature.query.filter_by(candidat_id=candidat.id, appel_id=appel.id).first()
        if not candidature:
            candidature = Candidature(
                candidat_id=candidat.id,
                appel_id=appel.id
            )
            db.session.add(candidature)
        
        # Mettre à jour les scores de la candidature
        candidature.score = score_total
        candidature.score_criteres = score_criteres
        candidature.score_experience = score_experience
        candidature.date_soumission = datetime.utcnow()

        db.session.commit()

        flash(" Votre candidature a bien été enregistrée et votre profil a été mis à jour.", "success")
        return redirect(url_for('candidat.afficher_formulaire', lien=lien))

    except Exception as e:
        db.session.rollback()
        flash(f" Erreur lors de la soumission : {str(e)}", "danger")
        # Log l'erreur pour le débogage
        print(f"Erreur lors de la soumission du formulaire : {e}")
        return redirect(url_for('candidat.afficher_formulaire', lien=lien))

@candidat_bp.route('/appel/<int:appel_id>/candidatures')
def list_candidatures(appel_id):
    """
    Affiche la liste des candidatures classées pour un appel donné.
    """
    appel = Appel.query.get_or_404(appel_id)
    # Récupération des candidatures et jointure avec les données des candidats
    candidatures = db.session.query(Candidature, Candidat) \
                             .join(Candidat) \
                             .filter(Candidature.appel_id == appel_id) \
                             .order_by(Candidature.score.desc()) \
                             .all()
    
    resultats = []
    for candidature, candidat in candidatures:
        resultats.append({
            'candidat': candidat,
            'date_soumission': candidature.date_soumission,  # Ajoutez cette ligne
            'score_criteres': candidature.score_criteres,
            'score_experience': candidature.score_experience,
            'score': candidature.score
        })
    
    return render_template("candidatures_par_appel.html", appel=appel, resultats=resultats)

@candidat_bp.route('/candidats')
def all_candidatures():
    """
    Affiche la liste de toutes les candidatures pour tous les appels.
    Permet de filtrer par appel ou par critère.
    """
    # Récupérer toutes les candidatures avec les informations du candidat et de l'appel
    candidatures = db.session.query(Candidature, Candidat, Appel) \
                             .join(Candidat, Candidature.candidat_id == Candidat.id) \
                             .join(Appel, Candidature.appel_id == Appel.id) \
                             .all()
    
    # Préparer les données pour le template
    resultats = []
    for candidature, candidat, appel in candidatures:
        resultats.append({
            'candidat': candidat,
            'appel_titre': appel.titre,
            'score': candidature.score
        })

    # Récupérer la liste des appels pour le filtre
    appels = Appel.query.all()
    
    return render_template('tous_candidats.html', candidatures=resultats, appels=appels)

# app/routes/candidat_routes.py

from fpdf import FPDF
from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, send_file
from io import BytesIO


@candidat_bp.route('/download/pdf/<int:appel_id>')
def download_pdf(appel_id):
    appel = Appel.query.get_or_404(appel_id)
    candidatures = db.session.query(Candidature, Candidat).join(Candidat).filter(Candidature.appel_id == appel_id).order_by(Candidature.score.desc()).all()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Titre du document
    pdf.cell(200, 10, txt=f"Classement des candidatures pour : {appel.titre}", ln=True, align='C')
    pdf.ln(10)

    # En-têtes du tableau
    headers = ["Rang", "Nom", "Prénom", "Score Total"]
    col_widths = [15, 40, 40, 30]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
    pdf.ln()

    # Données du tableau
    for i, (candidature, candidat) in enumerate(candidatures, 1):
        pdf.cell(col_widths[0], 10, str(i), 1, 0, 'C')
        pdf.cell(col_widths[1], 10, candidat.nom, 1, 0, 'L')
        pdf.cell(col_widths[2], 10, candidat.prenom, 1, 0, 'L')
        pdf.cell(col_widths[3], 10, f"{candidature.score:.2f}", 1, 0, 'C')
        pdf.ln()
    
    # Création du fichier PDF en mémoire
    output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin-1')  # Convertir la chaîne en octets
    output.write(pdf_bytes)
    output.seek(0)
    
    filename = f"classement_{appel.titre.replace(' ', '_').lower()}.pdf"
    
    # Renvoyer le PDF en tant que fichier téléchargeable
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/pdf')

@candidat_bp.route('/download/excel/<int:appel_id>')
def download_excel(appel_id):
    appel = Appel.query.get_or_404(appel_id)
    candidatures = db.session.query(Candidature, Candidat).join(Candidat).filter(Candidature.appel_id == appel_id).order_by(Candidature.score.desc()).all()

    data = []
    for i, (candidature, candidat) in enumerate(candidatures, 1):
        data.append({
            'Rang': i,
            'Nom': candidat.nom,
            'Prénom': candidat.prenom,
            'Email': candidat.email,
            'Téléphone': candidat.telephone,
            'Date de soumission': candidature.date_soumission.strftime('%d/%m/%Y à %H:%M'),
            'Score total': candidature.score
        })

    df = pd.DataFrame(data)

    # Création du fichier Excel en mémoire
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Classement')
    output.seek(0)

    filename = f"classement_{appel.titre.replace(' ', '_').lower()}.xlsx"
    return send_file(output, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')