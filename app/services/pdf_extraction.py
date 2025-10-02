# app/services/pdf_extraction.py
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrait le texte d'un fichier PDF.
    
    Args:
        pdf_path (str): Le chemin vers le fichier PDF.
        
    Returns:
        str: Le texte extrait du PDF.
    """
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte du PDF : {e}")
        # En production, vous pourriez vouloir lever une exception
        # ou renvoyer un message d'erreur différent.
        
    return text