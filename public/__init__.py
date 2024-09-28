from flask import Flask, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from os import path
from functools import wraps
from flask_login import LoginManager, login_required, current_user
from .config import SECRET_KEY, DB_NAME

db = SQLAlchemy()

def create_app():
    """Creates and configures the flask app to launch"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
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

def login_required_with_password_expiration(f):
    @wraps(f)
    @login_required
    def login_with_expiration(*args, **kwargs):
        # get most recent password
        # check if now is < expiration date
        # notify user to change if expiration is one week or less
        
        return f(*args, **kwargs)
    return login_with_expiration

def create_database(app):
    """Creates the database using the predefined models"""
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)