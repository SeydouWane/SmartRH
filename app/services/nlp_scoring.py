# app/services/nlp_scoring.py
import numpy as np
from sentence_transformers import SentenceTransformer, util
import re

# Charge un modèle de Hugging Face pour les embeddings
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_text_embeddings(text: str):
    """Génère l'embedding d'un texte."""
    return model.encode(text, convert_to_tensor=True)

def calculate_semantic_score(cv_text: str, criteres: list):
    """
    Calcule le score sémantique en comparant le CV aux critères.

    Args:
        cv_text (str): Le texte extrait du CV.
        criteres (list): Une liste de dictionnaires, chaque dict contenant
                         l'intitulé du critère et son score (poids).
    
    Returns:
        float: Le score sémantique total normalisé sur 100.
        dict: Les critères correspondants et leur score trouvé.
    """
    # 1. Vérifie si le texte du CV est valide
    if not cv_text:
        return 0.0, {}

    # 2. Divise le CV en phrases pour une analyse plus fine
    cv_sentences = re.split(r'[.!?]', cv_text)
    cv_sentences = [sentence.strip() for sentence in cv_sentences if len(sentence.strip()) > 10]
    
    if not cv_sentences:
        return 0.0, {}

    cv_embeddings = get_text_embeddings(cv_sentences)

    total_possible_score = sum(c['score'] for c in criteres)
    found_criteres_score = 0
    criteres_found = {}

    # 3. Itere sur chaque critère
    for critere in criteres:
        critere_intitule = critere['intitule']
        critere_score = critere['score']

        critere_embedding = get_text_embeddings(critere_intitule)
        
        # 4. Calcule la similarité entre le critère et toutes les phrases du CV
        similarities = util.cos_sim(critere_embedding, cv_embeddings)[0]

        # 5. Trouve la phrase la plus pertinente et prend son score de similarité
        best_similarity = np.max(similarities.cpu().numpy())
        
        # Le seuil de 0.5 est un bon point de départ. Si vous voulez des correspondances plus précises,
        # vous pouvez l'augmenter à 0.6 ou 0.7.
        if best_similarity > 0.5:
            # Ajoute le score pondéré du critère
            found_criteres_score += critere_score
            criteres_found[critere_intitule] = best_similarity

    # 6. Normalise le score final sur 100
    if total_possible_score > 0:
        score_percentage = (found_criteres_score / total_possible_score) * 100
    else:
        score_percentage = 0.0
    
    return score_percentage, criteres_found