# app/services/file_extraction.py
import os
import docx2txt
from PIL import Image
import pytesseract
import PyPDF2 # Ou pdfplumber, si vous préférez


def extract_text_from_pdf(filepath: str) -> str:
    """Extrait le texte d'un fichier PDF."""
    try:
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Erreur d'extraction PDF: {e}")
        return ""

def extract_text_from_docx(filepath: str) -> str:
    """Extrait le texte d'un fichier DOCX."""
    try:
        text = docx2txt.process(filepath)
        return text
    except Exception as e:
        print(f"Erreur d'extraction DOCX: {e}")
        return ""

def extract_text_from_image(filepath: str) -> str:
    """Extrait le texte d'un fichier image (via OCR)."""
    try:
        text = pytesseract.image_to_string(Image.open(filepath), lang='fra+eng')
        return text
    except Exception as e:
        print(f"Erreur d'extraction d'image (OCR): {e}")
        return ""

def extract_text_from_txt(filepath: str) -> str:
    """Extrait le texte d'un fichier TXT."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Erreur d'extraction TXT: {e}")
        return ""

def extract_text_from_file(filepath: str) -> str:
    """
    Extrait le texte en fonction de l'extension du fichier.
    Retourne une chaîne vide si le format n'est pas supporté.
    """
    _, file_extension = os.path.splitext(filepath)
    file_extension = file_extension.lower()

    if file_extension == '.pdf':
        return extract_text_from_pdf(filepath)
    elif file_extension == '.docx':
        return extract_text_from_docx(filepath)
    elif file_extension in ['.png', '.jpg', '.jpeg']:
        return extract_text_from_image(filepath)
    elif file_extension == '.txt':
        return extract_text_from_txt(filepath)
    else:
        print(f"Format de fichier non supporté: {file_extension}")
        return ""