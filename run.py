import os # Assurez-vous d'importer 'os' en haut du fichier si ce n'est pas déjà fait
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Ceci est la ligne cruciale que vous voulez conserver
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)