from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Qqmkl%408345@localhost:5432/rh_cv_platform'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    # Import des modèles et enregistrement des blueprints dans le contexte
    with app.app_context():
        from app.models import User  # ⬅️ Import ici
        from app.routes.auth_routes import auth_bp
        from app.routes.appel_routes import appel_bp
        from app.routes.candidat_routes import candidat_bp
        from app.routes.classement_routes import classement_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(appel_bp)
        app.register_blueprint(candidat_bp)
        app.register_blueprint(classement_bp)

        # Enregistrement du user_loader après import
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    return app

    return app
