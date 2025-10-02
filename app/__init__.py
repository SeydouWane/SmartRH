# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Qqmkl%408345@localhost:5432/rh_cv_platform'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuration des messages flash
    app.config['BOOTSTRAP_MSG_STYLE'] = True

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Définition de la vue de connexion
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

    # Importation des modèles et des Blueprints
    from app.models import User
    from app.routes.auth_routes import auth_bp
    from app.routes.appel_routes import appel_bp
    from app.routes.candidat_routes import candidat_bp
    from app.routes.classement_routes import classement_bp
    from app.routes.main_routes import main_bp

    # Enregistrement des Blueprints avec leurs préfixes URL
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(appel_bp, url_prefix='/appel')
    app.register_blueprint(candidat_bp, url_prefix='/candidat')
    app.register_blueprint(classement_bp, url_prefix='/classement')
    app.register_blueprint(main_bp, url_prefix='/')

    # Enregistrement du user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app