from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from .config import EMAILAPIKEY, FROMEMAIL
from .models import User
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content
from premailer import Premailer
email = Blueprint('email', __name__)

def sendEmail(toEmails: list[str], subject:str, body:str):
    """
    Sends an email with the :subject: and :body: to the :toEmails: from the 
    FROMEMAIL in config.py.
    """
    message = Mail(
        from_email=FROMEMAIL,
        to_emails=toEmails,
        subject=subject,
        html_content=Content("text/html", body)
    )
    try:
        return SendGridAPIClient(EMAILAPIKEY).send(message)
    except Exception as e:
        flash(e.message, category='error')
        return None
    

def sendEmailToAllUsersWithRole(company_id, role, subject, body):
    """Sends an email with :subject: and :body: to all users with at least
    the role ranking of :role: in the company with :company_id:"""
    role_hierarchy = {
        'administrator': ['administrator'],
        'manager': ['manager', 'administrator'],
        'user': ['user', 'manager', 'administrator']
    }
    
    toEmails = [user.email for user in User.query.filter(
        User.company_id == company_id,
        User.role.in_(role_hierarchy[role])
    ).all()]
    
    return sendEmail(toEmails=toEmails, subject=subject, body=body)


def getEmailHTML(user_id: int, pathToHTML):
    """Loads and returns HTML with inline CSS from external stylesheet"""
    # if you have a good few hours of extra time, and you want to deal with CSS,
    # you can work on getting the emails to look right with CSS
    
    # with open('public/static/style.css', 'r') as f:
    #     css_content = f.read()
        
    html_content = render_template(
        pathToHTML,
        userInfo=User.query.filter_by(id=user_id).first(),
        accountURL=url_for('views.user', id=user_id, _external=True)
    )
    
    return Premailer(
        html=html_content
        # css_text=css_content
    ).transform()


@email.route('/send', methods=['GET', 'POST'])
@login_required
def send():
    """Loads the Admin Email page and handles its logic"""
    emailFromUserPage = None
    try:
        emailFromUserPage = User.query.filter_by(
            id=int(request.args.get('id'))
        ).first().email
    except Exception as e:
        pass # if the user id is not valid, don't display an email

    if request.method == 'POST' and current_user.role == 'administrator':
        
        toEmail = request.form.get('toEmail')
        if toEmail == '':
            flash('Please select an email.', category='error')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        response = sendEmail(toEmails=toEmail, subject=subject, body=body)
        
        if response.status_code == 202:
            flash('Successfully delivered message', category='success')
            return redirect(url_for('views.home'))
        else:
            flash(f'Failed to deliver message. Status code: {response.status_code}', category='error')
            return redirect(url_for('views.home'))
    
    def getOptions():
        options = f'<option value="" {"selected" if not emailFromUserPage else ""}>Select an email</option>'
        for userOfApp in User.query.filter(User.company_id == current_user.company_id).all():
            options += f'\n<option value="{userOfApp.email}" {"selected" if emailFromUserPage == userOfApp.email else ""}>{userOfApp.username}: {userOfApp.email}</option>'
        return options
    
    return render_template(
        "email.html",
        options=getOptions(),
        user=current_user,
        dashUser=current_user.role,
        homeRoute='/',
        helpRoute="/help",
        back = url_for('views.home')
    )