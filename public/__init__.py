from flask import Flask, render_template,request,jsonify
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from .config import SECRET_KEY, DB_NAME

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'        
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
#failed attempt to implement email
    ''' # Configure Flask-Mail
    app.config['MAIL_SERVER'] = 'live.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'andresfelipec12@yahoo.com'
    app.config['MAIL_PASSWORD'] = '39f7259417efff58c1a03e5b34f092d7'

    mail = Mail(app)
    #attempted to use javascript to bring data over from email form but was unable to get it working 
    @app.route('/send_email', methods=['GET','POST'])
    def send():
        message = Message(
            subject='Hello',
            recipients=['andresfelipec12@yahoo.com'],
            sender='andresfelipec12@yahoo.com'
        )
        message.body = "hey"
        send(message)
        return "message sent!

        data = request.get_json()
        recipient = data['email']
        subject = data['subject']
        body = data['message']
        
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient])
        msg.body = body
        try:
            mail.send(msg)
            return jsonify({'status': 'Email sent successfully'})
        except Exception as e:
            return jsonify({'status': f'Failed to send email: {str(e)}'}), 500'''



    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

    

    if __name__ == '__main__':
        app.run(debug=True)
