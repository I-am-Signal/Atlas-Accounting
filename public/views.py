from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import User, Credential, Company, Suspension
from . import db
from datetime import datetime
import json


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # code for the dashboard
    
    # this is the old tutorial code, use as a reference if getting started
    # if request.method == 'POST': 
    #     note = request.form.get('note')#Gets the note from the HTML 

    #     if len(note) < 1:
    #         flash('Note is too short!', category='error') 
    #     else:
    #         new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
    #         db.session.add(new_note) #adding the note to the database 
    #         db.session.commit()
    #         flash('Note added!', category='success')
    adminAccessible = ''
    if 'administrator' == current_user.role:
        viewUsersLink = url_for('views.view_users')
        adminAccessible=f'<button class="dashleft admin"><a href="{viewUsersLink}">View/Edit Users</a></button>'
    
    eventLogsLink = '#'
    journalEntriesLink = '#'
    insertValueLink = '#'
    
    return render_template(
        "home.html",
        user=current_user,
        homeRoute='/',
        buttons=f'''{adminAccessible}
            <button class="dashleft"><a href="{eventLogsLink}">Event Logs</a></button>
            <button class="dashleft"><a href="{journalEntriesLink}">Journal Entries</a></button>
            <button class="dashleft"><a href="{insertValueLink}">Insert Value</a></button>
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
            
        table += '''
                </tbody>
            </table>
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
    return render_template(
        "home.html",
        user=current_user,
        homeRoute='/'
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

    userInfo = User.query.filter_by(id=user_id).first()
    
    if request.method == 'POST':
        userInfo.is_activated = bool(request.form.get('is_activated'))
        userInfo.username = request.form.get('username')
        userInfo.first_name = request.form.get('first_name')
        userInfo.last_name = request.form.get('last_name')
        userInfo.email = request.form.get('email')
        userInfo.addr_line_1 = request.form.get('address_line_1')
        userInfo.addr_line_2 = request.form.get('address_line_2')
        userInfo.city = request.form.get('city')
        userInfo.county = request.form.get('county')
        userInfo.state = request.form.get('state')
        userInfo.zipcode = request.form.get('zipcode')
        userInfo.dob = datetime.strptime(request.form.get('dob'), "%Y-%m-%d")
        
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
                    <option value='True' {'selected' if userInfo.is_activated == True else False}>True</option>
                    <option value='Talse' {'selected' if userInfo.is_activated == False else True}>False</option>
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
                <input id='addr_line_2' name='addr_line_2' value="{userInfo.addr_line_2}"><br>

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
                <button type='cancel'>Cancel Changes</button>
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
    return render_template(
        "home.html",
        user=current_user,
        homeRoute='/'
    )

# Old tutorial method, use as reference for building new ones
# @views.route('/delete-note', methods=['POST'])
# def delete_note():  
#     note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
#     noteId = note['noteId']
#     note = Note.query.get(noteId)
#     if note:
#         if note.user_id == current_user.id:
#             db.session.delete(note)
#             db.session.commit()

#     return jsonify({})