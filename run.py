import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Récupère le port de la variable d'environnement 'PORT', ou utilise 5000 par défaut.
    # Définit l'hôte sur '0.0.0.0' pour l'accès externe.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
