from flask import Blueprint, render_template, request, flash, redirect, url_for, get_flashed_messages
from flask_login import login_user, login_required, logout_user, current_user
from functools import wraps
from .models import User, Credential, Company
from . import db
from .email import sendEmailToAllUsersWithRole, getEmailHTML
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import desc
from enum import Enum

auth = Blueprint('auth', __name__)


def checkRoleClearance(user_role, role_required, templateIfClear=None):
    class Role(Enum):
        USER=1
        MANAGER=2
        ADMINISTRATOR=3    
    
    if Role[user_role.upper()].value < Role[role_required.upper()].value:
        flash('Your account does not have the right clearance for this page.')
        return redirect(url_for('views.home'))
    return templateIfClear


def login_required_with_password_expiration(f):
    @wraps(f)
    @login_required
    def login_with_expiration(*args, **kwargs):
        link_html = f'<a href="{
                url_for('auth.update_password')
            }"> Click here</a>'

        curr_pass = Credential.query.filter_by(
            user_id=current_user.id
        ).order_by(desc(Credential.create_date)).first()
        
        # password has expired
        if datetime.now() >= curr_pass.expirationDate:
            get_flashed_messages() # clears the login success message
            flash((f'Your password has expired. Please use forgot password to change your password.'))
            # no idea if this will actually log you out if password has expired
            return redirect(url_for('auth.logout')) 
        
        # password will expire with 7 days
        elif datetime.now() > (curr_pass.expirationDate - timedelta(days=7)):
            flash ((f'Password will expire soon. {link_html}'))
        
        return f(*args, **kwargs)
    return login_with_expiration


def checkIfPassIsValid(password):
        if len(password) < 8:
            return 'Password must be at least 8 characters.'
        elif not password[0].isalpha():
            return 'Password must begin with an alphabetical letter.'
        
        hasLetter = False
        hasNumber = False
        hasSpecial = False
        
        specialChars = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/\\"
        
        for char in password:
            if char.isalpha():
                hasLetter = True
            elif char.isdigit():
                hasNumber = True
            elif char in specialChars:
                hasSpecial = True
        if not hasLetter:
            return 'Password must contain at least one letter.'
        elif not hasNumber:
            return 'Password must contain at least one number.'
        elif not hasSpecial:
            return 'Password must contain at least one special character.'
        
        return 'valid'


def checkAllPreviousPasswords(passToCheck, user_id):
    previous_passwords = Credential.query.filter_by(
        user_id=user_id
    ).order_by(desc(Credential.create_date)).all()
    
    for password_hash in previous_passwords:
        if check_password_hash(password_hash.password, passToCheck):
            return True
    return False


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Loads the Login page and handles its logic"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        def checkIfAccountCanLogIn(user):
            if not user: # is this a valid username
                flash('Username does not exist.', category='error')
                return False
            
            if not True == user.is_activated: # has account been activated
                flash('Account is not currently active. Please contact your Company administrator.', category='error')
                return False

            # need to implement code to check for activate suspension
            suspended = False
            if suspended: # is this account suspended
                flash('Account is currently suspended. Please contact your Company administrator.', category='error')
            
            return True
        
        if checkIfAccountCanLogIn(user):
            try:
                password_entry = Credential.query.filter_by(
                    user_id=user.id
                ).order_by(desc(Credential.create_date)).first()
                
                if check_password_hash(password_entry.password, password) and password_entry.failedAttempts < 3:
                    login_user(user, remember=True)
                    flash('Logged in successfully!', category='success')
                    password_entry.failedAttempts = 0
                    return redirect(url_for('views.home'))
                elif password_entry.failedAttempts < 2:
                    flash('Incorrect password, try again.', category='error')
                    password_entry.failedAttempts += 1
                else:
                    flash('Incorrect password was used 3 or more times. Your account is now deactivated. Please contact your Company administrator.')
                    password_entry.failedAttempts += 1
                    user.is_activated = False
                db.session.commit()
            except Exception as e:
                flash(f'Error: {e}')
    
    return render_template("login.html", user=current_user, homeRoute='/login')


@auth.route('/logout')
@login_required
def logout():
    """Logs out the current user"""
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """Loads the Sign Up page and handles its logic"""
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        addr_line_1 = request.form.get('addr_line_1')
        addr_line_2 = request.form.get('addr_line_2')
        city = request.form.get('city')
        state = request.form.get('state')
        dob = request.form.get('dob')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        company_id = request.form.get('company_id')

        password_validity = checkIfPassIsValid(password1)

        user = User.query.filter_by(email=email).first()
        if user:
            flash(f'Email already exists with Company #{user.company_id}', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif len(addr_line_1) < 5:
            flash('Address Line 1 must be greater than 5 characters.', category='error')
        elif len(addr_line_2) < 5 and len(addr_line_2) > 0:
            flash('Address Line 2 must be greater than 5 characters.', category='error')
        elif len(city) < 2:
            flash('City must be greater than 1 character.', category='error')
        elif len(state) != 2:
            flash('State must be 2 characters.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif 'valid' != password_validity:
            flash(password_validity, category='error')
        else:
            new_user = User(
                email=email,
                first_name=first_name, 
                last_name=last_name,
                addr_line_1=addr_line_1,
                addr_line_2=addr_line_2 if len(addr_line_1) > 5 else '',
                city=city,
                state=state,
                dob=datetime.strptime(dob, "%Y-%m-%d"),
                username= f'{first_name[0]}{last_name}{datetime.now().strftime("%m%y")}',
                company_id=company_id
            )
            db.session.add(new_user)
            user = User.query.filter_by(email=email, username=f'{first_name[0]}{last_name}{datetime.now().strftime("%m%y")}').first()
            
            new_pass = Credential(
                user_id=user.id,
                password=generate_password_hash(
                    password1, method='pbkdf2:sha256'
                )
            )
            
            if not company_id:
                # user needs to be logged in ONLY if company id is blank, meaning that
                # the new user is the administrator for their newly created company
                user.role = 'administrator'
                user.is_activated = True
                new_company = Company(
                    creator_of_company=user.id
                )
                db.session.add(new_company)
                user.company_id = Company.query.filter_by(creator_of_company=user.id).first().id
                login_user(new_user, remember=True)
                flash(f'Account created with username {user.username}! Welcome to Atlas Accounting.', category='success')
            else:
                flash(f'Account was created with username {user.username}. Please contact your Company administrator for account activation. Welcome to Atlas Accounting.', category='success')
                response = sendEmailToAllUsersWithRole(
                    company_id=user.company_id,
                    role='administrator',
                    subject='New User',
                    body=getEmailHTML(user.id, "email_templates/new_user.html")
                )
                if not response.status_code == 202:
                    flash(f'Failed to deliver message to admin. Status code: {response.status_code}', category='error')
            
            db.session.add(new_pass)
            db.session.commit()
            return redirect(url_for('auth.login'))

    return render_template("sign_up.html", user=current_user, homeRoute='/login')


@auth.route('/forgot', methods=['GET', 'POST'])
def forgot():
    """Loads the Forgot Password? page and handles its logic"""
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        
        user = User.query.filter_by(email=email, username=username).first()
        
        if user:
            # Send email logic (implement this function to send email)
            # sendResetEmail(user)
            flash('Implement email and reset logic', category='success')
            # flash('A reset email has been sent!', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('No account found with that email and username combination.', category='error')
        db.session.commit()

    return render_template(
      "forgot.html",
      user=current_user,
      homeRoute='/login'
    )


@auth.route('/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    """Loads the update password page and handles its logic"""
    if request.method == 'POST':      
        
        previous_password = Credential.query.filter_by(
            user_id=current_user.id
        ).order_by(desc(Credential.create_date)).first()

        curr_password = request.form.get('password')
        newpassword = request.form.get('newpassword')
        confirmpassword = request.form.get('confirmpassword')
        
        password_validity = checkIfPassIsValid(newpassword)
        
        # check if curr_password from form is the same as saved current password
        if not check_password_hash(previous_password.password, curr_password):
            flash('Original password was incorrect.', category='error')
        elif 'valid' != password_validity: # check if new password is valid
            flash(password_validity, category='error')
        elif checkAllPreviousPasswords(newpassword, current_user.id): # check if new password == an old one
            flash('New password cannot be a previously used password.')
        elif newpassword != confirmpassword: # check if new == confirm
            flash('New Password and Confirmation must match.', category='error')
        else:
            new_pass = Credential(
                user_id=current_user.id,
                password=generate_password_hash(
                    newpassword, method='pbkdf2:sha256'
                )
            )
            
            db.session.add(new_pass)
            db.session.commit()
            flash('Your password was updated successfully.')
            return redirect(url_for('views.home'))
    
    return render_template(
        "update_password.html", 
        user=current_user,
        homeRoute='/'
    )
