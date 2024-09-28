<<<<<<< HEAD
<<<<<<< HEAD
from flask import Flask, render_template, flash
=======
from flask import Flask, render_template
>>>>>>> a43b7e9 (Alembic is setup (i think), new additions to input validation for viewing users, error page and 404 handling)
=======
from flask import Flask, render_template, flash
>>>>>>> 39d1701 (Email and Suspension Additions (neither is complete))
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
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
<<<<<<< HEAD
<<<<<<< HEAD
        """Loads the 404 page"""
=======
>>>>>>> a43b7e9 (Alembic is setup (i think), new additions to input validation for viewing users, error page and 404 handling)
=======
        """Loads the 404 page"""
>>>>>>> 39d1701 (Email and Suspension Additions (neither is complete))
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