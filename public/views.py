from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from markupsafe import Markup
from flask_login import login_required, current_user
from .models import User, Credential, Company, Suspension
from werkzeug.security import  check_password_hash
from . import db
from datetime import datetime,timedelta
import json


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    adminAccessible = ''
    if 'administrator' == current_user.role:
        viewUsersLink = url_for('views.view_users')
        adminAccessible=f'<a href="{viewUsersLink}"><button class="dashleft admin">View/Edit Users</button></a>'
    
    eventLogsLink = '#'
    journalEntriesLink = '#'
    insertValueLink = '#'
    testEmailLink = url_for('email.send')
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> fdb32fc (weird spaces)
    updatePasswordLink = url_for('auth.update_password', username = current_user.username)
    link_html = f'<a href="{updatePasswordLink}"> Click here</a>'

    #change to actual experiation date after testing is done 
    current_time = datetime.now()
    expire_date = current_user.create_date + timedelta(minutes=10)
    flash(expire_date)
    flash(current_time)
    
    if current_time >= (expire_date - timedelta(minutes=3)):
        flash ((f'Password is about to Expire {link_html}'))  
    elif current_time >= expire_date:
        flash((f'Password is Expired {link_html}'))  
        #abstract to login required

<<<<<<< HEAD
=======
>>>>>>> 39d1701 (Email and Suspension Additions (neither is complete))
=======
>>>>>>> fdb32fc (weird spaces)
    
    return render_template(
        "home.html",
        user=current_user,
        homeRoute='/',
        buttons=f'''{adminAccessible}
            <a href="{eventLogsLink}"><button class="dashleft">Event Logs</button></a>
            <a href="{journalEntriesLink}"><button class="dashleft">Journal Entries</button></a>
            <a href="{insertValueLink}"><button class="dashleft">Insert Value</button></a>
            <a href="{testEmailLink}"><button class="dashleft">Test Email</button></a>
        '''
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
                    <td>{user.email}</td>
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
    
    if 'administrator' == current_user.role:
        return render_template(
            "view_users.html",
            user=current_user,
            homeRoute='/',
            users=generateUsers()
        )
    
    flash('Your account does not have the right clearance for this page.')
    return redirect(url_for('views.home'))


@views.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    user_id = request.args.get('id')
    try:
        user_id=int(user_id)
    except Exception as e:
        flash('Error: invalid user id')
        return redirect(url_for('auth.login'))

    userInfo = User.query.filter_by(id=user_id).first()
    
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
            
            db.session.commit()
            flash('Information for User ' + userInfo.username + ' was successfully changed!', category='success')
            return redirect(url_for('views.view_users'))
        
    def getUserInfo():
        display = f'''
            <a href='{url_for('views.view_users')}'>Back</a> <br />
        
            <form method='POST'>
                <p>User ID: {userInfo.id}</p>
                
                <label for='is_activated'>Activated</label>
                <select id='is_activated' name='is_activated'>
                    <option value='True' {'selected' if userInfo.is_activated else ''}>True</option>
                    <option value='False' {'selected' if not userInfo.is_activated else ''}>False</option>
                </select><br>
                
                <label for='username'>Username</label>
                <input id='username' name='username' value={userInfo.username}><br>
                
                <label for='first_name'>First Name</label>
                <input id='first_name' name='first_name' value={userInfo.first_name}><br>
                
                <label for='last_name'>Last Name</label>
                <input id='last_name' name='last_name' value={userInfo.last_name}><br>
                
                <label for='email'>Email</label>
                <input id='email' name='email' value={userInfo.email}><br>

                <label for='addr_line_1'>Address Line 1</label>
                <input id='addr_line_1' name='addr_line_1' value="{userInfo.addr_line_1}"><br>

                <label for='addr_line_2'>Address Line 2</label>
                <input id='addr_line_2' name='addr_line_2' value="{'' if userInfo.addr_line_2 == None else userInfo.addr_line_2}"><br>

                <label for='city'>City</label>
                <input id='city' name='city' value="{userInfo.city}"><br>

                <label for='county'>County</label>
                <input id='county' name='county' value="{userInfo.county}"><br>

                <label for='state'>State</label>
                <input id='state' name='state' value="{userInfo.state}"><br>
                
                <label for='dob'>Date of Birth</label>
                <input id='dob' name='dob' type="date" value="{userInfo.dob}"><br>

                <label for='role'>Role</label>
                <select id='role' name='role'>
                    <option value='administrator' {'selected' if userInfo.role == 'administrator' else ''}>Administrator</option>
                    <option value='manager' {'selected' if userInfo.role == 'manager' else ''}>Manager</option>
                    <option value='user' {'selected' if userInfo.role == 'user' else ''}>User</option>
                </select><br>

                <button type='submit'>Submit</button>
                <button type='button' onclick="window.location.href='{ 
                    url_for('views.view_users')
                }'">Cancel Changes</button>
<<<<<<< HEAD
<<<<<<< HEAD
                <button type='button' onclick="window.location.href='{
                    url_for('suspend.suspensions', id=userInfo.id)
                }'">View Suspensions</button>
=======
>>>>>>> a43b7e9 (Alembic is setup (i think), new additions to input validation for viewing users, error page and 404 handling)
=======
                <button type='button' onclick="window.location.href='{
                    url_for('suspend.suspensions', id=userInfo.id)
                }'">View Suspensions</button>
>>>>>>> 39d1701 (Email and Suspension Additions (neither is complete))
            </form>
        '''
        return display
    
    if 'administrator' == current_user.role:
        return render_template(
            "user.html",
            user=current_user,
            homeRoute='/',
            user_viewed=getUserInfo()
        )
    
    flash('Your account does not have the right clearance within your Company to view this page.')
<<<<<<< HEAD
<<<<<<< HEAD
    return redirect(url_for('views.home'))

=======
    return redirect(url_for('views.home'))
>>>>>>> a43b7e9 (Alembic is setup (i think), new additions to input validation for viewing users, error page and 404 handling)
=======
    return redirect(url_for('views.home'))

>>>>>>> fdb32fc (weird spaces)
