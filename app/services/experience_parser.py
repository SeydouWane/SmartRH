# app/services/experience_parser.py
import re

def extract_experience_years(cv_text: str) -> int:
    """
    Extrait les années d'expérience d'un CV en texte.
    
    Args:
        cv_text (str): Le texte extrait du CV.
        
    Returns:
        int: Le nombre d'années d'expérience trouvées.
    """
    years = 0
    # Modèle pour trouver les années d'expérience (ex: '5 ans', '6+ ans')
    # Ceci est une version simplifiée. Un modèle plus complexe pourrait être nécessaire.
    matches = re.findall(r'(\d+)\s*an(s)?\s*d\'exp[eé]rience|exp[eé]rience\s*de\s*(\d+)\s*an(s)?', cv_text, re.IGNORECASE)
    
    if matches:
        # Extrait le premier nombre trouvé, si plusieurs
        years = int(matches[0][0] or matches[0][2])

    return years

def calculate_experience_score(years_of_experience):
    """
    Calcule le score d'expérience.
    Pour l'instant, retourne simplement le nombre d'années d'expérience,
    car il est saisi directement par le candidat.
    """
    return years_of_experience