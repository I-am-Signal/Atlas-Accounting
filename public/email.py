from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from .config import EMAILAPIKEY, FROMEMAIL
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
            user=current_user,
            homeRoute='/',
            emailStuff=f'''
            <div class='login'>
                <form method='POST'>
                    <p>Please don't send too many, we only get 100 per day</p>
                    <label for='toEmail'>Send to email:</label>
                    <input id='toEmail' name='toEmail'>
                    
                    <label for='subject'>Subject</label>
                    <input id='subject' name='subject'>
                    
                    <label for='body'>Body</label>
                    <input id='body' name='body'>
                    
                    <button id='test' name='test'>Submit</button>
                    <button type='button' onclick="window.location.href='{ 
                        url_for('views.home')
                    }'">Cancel Changes</button>
                </form>
            </div>
            '''
        )
    
    flash('Your account does not have the right clearance for this page.')
    return redirect(url_for('views.home'))