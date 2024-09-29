from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from .config import EMAILAPIKEY, FROMEMAIL
from .models import User
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

email = Blueprint('email', __name__)

def sendEmail(toEmails: list[str], subject:str, body:str):
    """Sends an email with the :subject: and :body: to the :toEmails: from the 
    FROMEMAIL in config.py."""
    message = Mail(
        from_email=FROMEMAIL,
        to_emails=toEmails,
        subject=subject,
        html_content=body
    )
    try:
        sg = SendGridAPIClient(EMAILAPIKEY)
        return sg.send(message)
    except Exception as e:
        flash(e.message,category='error')
        return None

# Just for testing, can be removed in production
@email.route('/send', methods=['GET', 'POST'])
@login_required
def send():
    """Loads the Test Email page and handles its logic"""
    try:
        emailFromUserPage = User.query.filter_by(
            id=int(request.args.get('id'))
        ).first().email
    except Exception as e:
        pass # if the user id is not valid, don't display an email

    if request.method == 'POST' and current_user.role == 'administrator':
        
        toEmail = request.form.get('toEmail')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        response = sendEmail(toEmails=toEmail, subject=subject, body=body)
        
        if response.status_code == 202:
            flash('Successfully delivered message', category='success')
            return redirect(url_for('views.home'))
        else:
            flash(f'Failed to deliver message. Status code: {response.status_code}', category='error')
            return redirect(url_for('views.home'))

    if 'administrator' == current_user.role:
        return render_template(
            "email.html",
            email=emailFromUserPage if emailFromUserPage else '',
            user=current_user,
            homeRoute='/',
            back = url_for('views.home')
        )
    
    flash('Your account does not have the right clearance for this page.')
    return redirect(url_for('views.home'))