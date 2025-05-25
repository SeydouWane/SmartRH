from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.models import db, User  # Reprendre l’instance existante !

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Qqmkl%408345@localhost:5432/rh_cv_platform'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # 👈 essentiel pour éviter ton erreur
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import et enregistrement des blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.appel_routes import appel_bp
    from app.routes.candidat_routes import candidat_bp
    from app.routes.classement_routes import classement_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(appel_bp)
    app.register_blueprint(candidat_bp)
    app.register_blueprint(classement_bp)

    return app
