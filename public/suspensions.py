from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import User, Credential, Company, Suspension
from . import db
from .auth import checkRoleClearance
from datetime import datetime, timedelta



suspend = Blueprint('suspend', __name__)


@suspend.route('/suspensions', methods=['GET', 'POST'])
@login_required
def suspensions():
    """Loads the Suspensions page and handles its logic"""
    user_id = request.args.get('id')
    try:
        user_id=int(user_id)
    except Exception as e:
        flash('Error: invalid user id')
        return redirect(url_for('auth.login'))

    userInfo = User.query.filter_by(id=user_id).first()

    def getSuspensionsInfo():
        display = f'''
            <div class="userDisplay">
                <a href='{ url_for('views.user', id=user_id) }'>Back</a>&nbsp;&nbsp;&nbsp;
                Suspension Information for <strong>{userInfo.username}</strong> <br />
                
                <table>
                    <thead>
                        <tr>
                            <th>Suspension ID</th>
                            <th>Suspension Start Date</th>
                            <th>Suspension End Date</th>
                            <th>Currently Active</th>
                        </tr>
                    </thead>
                    <tbody>
        '''
        
        display += f'''
            <tr>
                <td><a href="{url_for('suspend.suspension', id=user_id, suspension_id='new')}">Add New Suspension</a></td>
                <td></td>
                <td></td>
                <td></td>
            </tr>    
        '''
        
        suspensions = Suspension.query.join(
            User,
            Suspension.user_id == User.id
        ).filter(Suspension.user_id == user_id).all()
        
        for suspension in suspensions:
            display += f'''
                <tr>
                    <td><a href="{url_for('suspend.suspension', id=user_id, suspension_id=suspension.id)}">{suspension.id}</a></td>
                    <td>
                        <input 
                            id='suspension_end_date'
                            name='suspension_end_date'
                            type="datetime-local"
                            value="{suspension.suspension_start_date}" 
                            readonly">
                    </td>
                    <td>
                        <input 
                            id='suspension_end_date'
                            name='suspension_end_date'
                            type="datetime-local"
                            value="{suspension.suspension_end_date}" 
                            readonly">
                    </td>
                    <td>{'True' if suspension.suspension_start_date < datetime.now() < suspension.suspension_end_date else 'False'}
                </tr>
            '''
            
        display += f'''
                    </tbody>
                </table>
            </div>
        '''
        return display 
    
    return checkRoleClearance(current_user.role, 'administrator', render_template(
            "suspensions.html",
            user=current_user,
            dashUser=current_user.role,
            homeRoute='/',
            suspensionInfo=getSuspensionsInfo()
        )
    )



@suspend.route('/suspension', methods=['GET', 'POST'])
@login_required
def suspension():
    """Loads the individual Suspension page and handles its logic"""
    
    suspension_id = request.args.get('suspension_id')
    
    # MODULARIZE from here
    user_id = request.args.get('id')

    try:
        user_id=int(user_id)
    except Exception as e:
        flash(f'Error: invalid user id {user_id}', category='error')
        return redirect(url_for('views.view_users'))

    userInfo = User.query.filter_by(id=user_id).first()
    
    if not userInfo:
        flash(f'Error: user not found for id {user_id}')
        return redirect(url_for('views.view_users'))
    # MODULARIZE to here
    
    if request.method == 'GET':
        # display new suspension
        if suspension_id == 'new':      
            return checkRoleClearance(current_user.role, 'administrator', render_template(
                    "suspension.html",
                    user=current_user,
                    dashUser=current_user.role,
                    back=url_for('suspend.suspensions', id=user_id),
                    homeRoute='/',
                    start_date=(datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M'),
                    end_date=(datetime.now() + timedelta(days=1, minutes=5)).strftime('%Y-%m-%dT%H:%M')
                )
            )

        # display previous suspension
        if suspension_id != 'new':
            try:
                suspension_id=int(suspension_id)
                curr_suspension = Suspension.query.filter_by(id=suspension_id).first()
            
                return checkRoleClearance(current_user.role, 'administrator', render_template(
                        "suspension.html",
                        user=current_user,
                        dashUser=current_user.role,
                        back=url_for('suspend.suspensions', id=user_id),
                        homeRoute='/',
                        suspension_id = curr_suspension.id,
                        start_date=curr_suspension.suspension_start_date.strftime('%Y-%m-%dT%H:%M'),
                        end_date=curr_suspension.suspension_end_date.strftime('%Y-%m-%dT%H:%M')
                    )
                )
            except Exception as e:
                flash(f'Error: invalid suspension id: {suspension_id}', category='error')
                return redirect(url_for('views.view_users'))
    
    if request.method == 'POST': 
        suspension_start_date = datetime.strptime(request.form.get('suspension_start_date'), '%Y-%m-%dT%H:%M')
        suspension_end_date = datetime.strptime(request.form.get('suspension_end_date'), '%Y-%m-%dT%H:%M')
        
        if suspension_end_date < suspension_start_date:
            flash("End date must be on or after the start date.")
            return redirect(url_for('suspend.suspensions',id=user_id))
        
        if suspension_id == 'new': 
            # Ensure suspension start date is the current time or later
            if suspension_start_date < datetime.now():
                flash("Start date must be today or in the future.")
                return redirect(url_for('suspend.suspensions',id=user_id))
            
            new_suspension = Suspension(
                user_id=user_id,
                suspension_start_date=suspension_start_date,
                suspension_end_date=suspension_end_date
            )
            db.session.add(new_suspension)
            db.session.commit()
            flash(f'New suspension was added for user {userInfo.username}!', category='success')
            return redirect(url_for('suspend.suspensions', id=userInfo.id))
        
        
        if suspension_id != 'new':
            suspensionInfo = None
            try:
                suspension_id=int(suspension_id)
                suspensionInfo = Suspension.query.filter_by(id=suspension_id).first()
            except Exception as e:
                flash(f'Error: invalid user id {user_id}', category='error')
                return redirect(url_for('views.view_users'))
            
            if not suspensionInfo:
                flash(f'Error: Suspension not found with id: {suspension_id}')
                return redirect(url_for('views.view_users')) 
            
            # Update the fields
            if suspensionInfo:
                suspensionInfo.suspension_start_date = suspension_start_date
                suspensionInfo.suspension_end_date = suspension_end_date
            
            db.session.commit()
            flash(f'Suspension {suspensionInfo.id} for user {userInfo.username} was successfully added!', category='success')        
            return redirect(url_for('suspend.suspensions',id=userInfo.id))