from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Company, Credential
from . import db
from .auth import login_required_with_password_expiration, checkRoleClearance
from datetime import datetime
from sqlalchemy import desc


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required_with_password_expiration
def home():
    adminAccessible = None
    if 'administrator' == current_user.role:
        viewUsersLink = url_for('views.view_users')
        adminAccessible=f'<a href="{viewUsersLink}"><button class="dashleft admin">View/Edit Users</button></a>'
    
    eventLogsLink = '#'
    journalEntriesLink = '#'
    insertValueLink = '#'

    return checkRoleClearance(current_user.role, 'user', render_template(
            "home.html",
            user=current_user,
            homeRoute='/',
            viewUsersButton=adminAccessible if adminAccessible else '',
            eventLogsLink = eventLogsLink,
            journalEntriesLink=journalEntriesLink,
            insertValueLink=insertValueLink
        )
    )

@views.route('/view_users', methods=['GET', 'POST'])
@login_required
def view_users():
    def generateUsers():
        table = f'''
            <a href='{url_for('views.home')}'>Back</a> <br />
            
            <table class="userDisplay">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>First Name</th>
                        <th>Last Name</th>
                        <th>Email</th>
                        <th>Activated</th>
                        <th>Role</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for user in User.query.join(
            Company,
            User.company_id == Company.id
        ).filter(Company.id == current_user.company_id).all():
            table += f'''
                <tr>
                    <td>{user.id}</td>
                    <td><a href="{ url_for('views.user', id=user.id) }">{user.username}</a></td>
                    <td>{user.first_name}</td>
                    <td>{user.last_name}</td>
                    <td>{f"<a href='{url_for('email.send', id=user.id)}'>{user.email}</a>"}</td>
                    <td>{user.is_activated}</td>
                    <td>{user.role}</td>
                </tr>
            '''
            
        table += f'''
                </tbody>
            </table>
            <a href='{ url_for('auth.sign_up') }'>Create New User</a>
        '''
        return table 
    
    return checkRoleClearance(current_user.role, 'administrator', render_template
        (
            "view_users.html",
            user=current_user,
            homeRoute='/',
            users=generateUsers()
        )
    )


@views.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    user_id = request.args.get('id')
    try:
        user_id=int(user_id)
    except Exception as e:
        flash('Error: invalid user id')
        return redirect(url_for('auth.login'))
    
    curr_pass = Credential.query.filter_by(
        user_id=user_id
    ).order_by(desc(Credential.create_date)).first()

    userInfo = User.query.filter_by(id=user_id).first()
    
    userInfo.addr_line_2 = '' if userInfo.addr_line_2 == None else userInfo.addr_line_2
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        addr_line_1 = request.form.get('addr_line_1')
        addr_line_2 = request.form.get('addr_line_2')
        city = request.form.get('city')
        county = request.form.get('county')
        state = request.form.get('state')
        
        users = User.query.filter_by(email=email).limit(2).all()
        if users and (len(users) > 2 or users[0].id != userInfo.id):
            flash('Email cannot be the same as was used in a different account.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif len(addr_line_1) < 5:
            flash('Address Line 1 must be greater than 5 characters.', category='error')
        elif len(addr_line_2) < 5 and len(addr_line_2) > 0:
            flash('Address Line 2 must be greater than 5 characters or empty.', category='error')
        elif len(city) < 2:
            flash('City must be greater than 1 character.', category='error')
        elif len(county) < 2:
            flash('County must be greater than 1 character.', category='error')
        elif len(state) != 2:
            flash('State must be 2 characters.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        else:
            userInfo.is_activated = request.form.get('is_activated') == 'True'
            userInfo.username = request.form.get('username')
            userInfo.first_name = request.form.get('first_name')
            userInfo.last_name = request.form.get('last_name')
            userInfo.email = request.form.get('email')
            userInfo.addr_line_1 = request.form.get('addr_line_1')
            userInfo.addr_line_2 = request.form.get('addr_line_2')
            userInfo.city = request.form.get('city')
            userInfo.county = request.form.get('county')
            userInfo.state = request.form.get('state')
            userInfo.dob = datetime.strptime(request.form.get('dob'), "%Y-%m-%d")
            userInfo.role = request.form.get('role')
            
            curr_pass.expirationDate = datetime.strptime(request.form.get('start'), '%Y-%m-%dT%H:%M')
            
            db.session.commit()
            flash('Information for User ' + userInfo.username + ' was successfully changed!', category='success')
            return redirect(url_for('views.view_users'))
    
    return checkRoleClearance(current_user.role, 'administrator', render_template(
            "user.html",
            user=current_user,
            homeRoute='/',
            back=url_for('views.view_users'),
            userInfo=userInfo,
            testExpiration = curr_pass.expirationDate.strftime('%Y-%m-%dT%H:%M') if curr_pass.expirationDate else '',
            suspensions=url_for('suspend.suspensions', id=userInfo.id),
            delete=url_for('views.delete', id=userInfo.id)
        )
    )
    

@views.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    user_id = request.args.get('id')
    try:
        user_id=int(user_id)
    except Exception as e:
        flash('Error: invalid user id')
        return redirect(url_for('auth.login'))

    userInfo = User.query.filter_by(id=user_id).first()
    
    if request.method == 'POST':
        if request.form.get('delete') == 'True':
            usernameToBeDeleted = userInfo.username
            db.session.delete(userInfo)
            db.session.commit()
            flash('Information for User ' + usernameToBeDeleted + ' was successfully deleted!', category='success')
        return redirect(url_for('views.view_users'))
    
    return checkRoleClearance(current_user.role, 'administrator', render_template(
            "delete.html",
            user=current_user,
            homeRoute='/',
            back=url_for('views.view_users'),
            userInfo=userInfo
        )
    )