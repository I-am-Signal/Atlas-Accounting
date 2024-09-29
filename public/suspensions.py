from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import User, Credential, Company, Suspension
from . import db
from .auth import checkRoleClearance
from datetime import datetime
import json


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
    
    if request.method == 'POST':
        userInfo.role = request.form.get('role')
        
        db.session.commit()
        flash('Information for User ' + userInfo.username + ' was successfully changed!', category='success')
        return redirect(url_for('views.view_users'))

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
        
        suspensions = Suspension.query.join(
            User,
            Suspension.user_id == User.id
        ).filter(Suspension.user_id == user_id).all()
        
        display += f'''
            <tr>
                <td><a href="{url_for('suspend.suspension', id=user_id, suspension_id='new')}">Add New Suspension</a></td>
                <td></td>
                <td></td>
                <td></td>
            </tr>    
        '''
        
        for suspension in suspensions:
            display += f'''
                <tr>
                    <td><a href="{url_for('suspend.suspension', id=user_id)}">{suspension.id}</a></td>
                    <td>{suspension.suspension_start_date}</td>
                    <td>{suspension.suspension_end_date}</td>
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
        return redirect(url_for('auth.login'))

    userInfo = User.query.filter_by(id=user_id).first()
    
    if not userInfo:
        flash(f'Error: user not found for id {user_id}')
        return redirect(url_for('auth.login'))
    # MODULARIZE to here
    
    suspensionInfo = None
    if suspension_id == 'new':
        # handle suspensions that are not present in the db yet
        flash('Please implement handling new suspensions')
        return redirect(url_for('suspend.suspensions', id=user_id))
    
    
    # below handles suspension that are already present and being pulled from the db
    try:
        suspension_id_id=int(suspension_id_id)
    except Exception as e:
        flash('Error: invalid suspension id')
        return redirect(url_for('auth.login'))

    suspensionInfo = Suspension.query.filter_by(id=suspension_id).first()
    
    if not suspensionInfo:
        flash(f'Error: suspension not found for id {suspension_id}')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':        
        suspension_start_date = datetime.strptime(request.form.get('dob'), "%Y-%m-%d")
        suspension_end_date = datetime.strptime(request.form.get('dob'), "%Y-%m-%d")
        
        # ensure suspension start date is now or after
        # ensure end date is on or after start date
        
        # new_suspension = Suspension(
        #     user_id=user_id,
        #     suspension_start_date=suspension_start_date,
        #     suspension_end_date=suspension_end_date
        # )
        
        # db.session.add(new_suspension)
        # db.session.commit()
        # flash('Information for User ' + userInfo.username + ' was successfully changed!', category='success')
        flash('Please implement POST for editing individual suspension info', category='error')
        return redirect(url_for('views.view_users'))
    
    return checkRoleClearance(current_user.role, 'administrator', render_template(
            "suspension.html",
            user=current_user,
            back=url_for(' suspensions.suspensions', id=user_id),
            homeRoute='/',
            suspensionID=int(Suspension.query.order_by(Suspension.id.desc()).first()) + 1,
            start_date=suspensionInfo.suspension_start_date,
            end_date=suspensionInfo.suspension_end_date
        )
    )