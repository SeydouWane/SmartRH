from app import create_app, db

app = create_app()

with app.app_context():
    print("Initialisation de la base de données...")
    db.create_all()
    print(" Tables créées avec succès dans la base PostgreSQL.")
