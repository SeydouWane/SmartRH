from flask import Blueprint

classement_bp = Blueprint('classement', __name__)

@classement_bp.route('/classement')
def afficher_classement():
    return "Classement automatique des candidats"
