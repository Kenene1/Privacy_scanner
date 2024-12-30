import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from logging.handlers import RotatingFileHandler
import logging

# Initialize the extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()

def create_app(config_class=None):
    """App Factory for creating the app instance."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class or get_config())
    
    # Initialize the extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Set the login view and the 'unauthorized' handler
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Register Blueprints
    from app.routes import main
    from app.auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')

    # Set up logging
    setup_logging(app)

    return app

def get_config():
    """Get configuration settings."""
    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'defaultsecretkey')  # Replace with a real secret key in production
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')  # Example SQLite DB
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        MAIL_SERVER = os.environ.get('MAIL_SERVER')
        MAIL_PORT = 587
        MAIL_USE_TLS = True
        MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
        FLASK_ENV = os.environ.get('FLASK_ENV', 'development')  # For production, set to 'production'

    return Config

def setup_logging(app):
    """Set up logging for the application."""
    if not app.debug:
        # Ensure that the directory for the log file exists
        log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Set up the log file and rotation
        log_file = os.path.join(log_dir, 'app.log')
        handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        app.logger.addHandler(handler)

        # Log the startup of the application
        app.logger.info('Application startup')
