from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from .config import SECRET_KEY, DB_NAME, DOMAIN_NAME, APPLICATION_ROOT, PREFERRED_URL_SCHEME

db = SQLAlchemy()

def create_app():
    """Creates and configures the flask app to launch"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SERVER_NAME'] = DOMAIN_NAME
    app.config['APPLICATION_ROOT'] = APPLICATION_ROOT
    app.config['PREFERRED_URL_SCHEME'] = PREFERRED_URL_SCHEME
    
    db.init_app(app)

    # Updates these when new blueprints are created
    from .views import views
    from .auth import auth
    from .email import email
    from .suspensions import suspend

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(email, url_prefix='/')
    app.register_blueprint(suspend, url_prefix='/')

    # Update this when authentication via models changes
    from .models import User
    
    with app.app_context():
        db.create_all()
    
    # For Sprint 1 Requirement 15
    with app.app_context():
        start_scheduler(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        """Returns the currently logged in user"""
        return User.query.get(int(id))
    
    @app.errorhandler(404)
    def page_not_found(e):   

        """Loads the 404 page"""

        return render_template(
        "error.html",
        error_header='Error 404 - Page Not Found',
        error_msg='Sorry, the page you are looking for does not exist.',
        homeRoute='/'
    ), 404
    
    return app

def create_database(app):
    """Creates the database using the predefined models"""
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        
    
def start_scheduler(app):
    from apscheduler.schedulers.background import BackgroundScheduler
    
    def emailUsersWithExpiringPasswords():
        with app.app_context():
            from .models import Credential, User
            from datetime import datetime, timedelta
            from .email import sendEmail, getEmailHTML
            
            users = [user for user in User.query.join(
                    Credential,
                    User.id == Credential.user_id
                ).filter(
                    Credential.expirationDate <= datetime.now() + timedelta(days=3)
                ).all()
            ]
            
            for user in users:
                response = sendEmail(
                    toEmails=user.email,
                    subject='Password Expires Soon',
                    body=getEmailHTML(user.id, 'email_templates/expiring.html')
                )
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        emailUsersWithExpiringPasswords,
        'cron',
        hour=12,
        minute=30)
    scheduler.start()