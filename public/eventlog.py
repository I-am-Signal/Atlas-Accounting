from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Company, Credential, Account,Event

from .auth import  checkRoleClearance

from datetime import datetime
from sqlalchemy import desc, asc

eventlog = Blueprint('eventlog', __name__)

@eventlog.route('/view_eventlogs', methods=['GET'])
@login_required
def view_eventlogs():
        
    def generateLogs():
        
        table = f'''
            <a href='{url_for('views.home')}'>Back</a> <br />
            <table class="userDisplay">
                <thead>
                    <tr>
                        <th>Log ID</th> 
                        <th>Account Number</th>
                        <th>Account Name</th>                                          
                        <th>Change Made by: UserID </th>
                        <th>Date Modified</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for event in Event.query.filter(Event.id).order_by(asc(Event.number)).all():
            
            table += f'''
                <tr onclick="window.location.href='{url_for('eventlog.view_event',number=event.id)}'" style="cursor: pointer;">
                    
                    <td>{event.id}</td>
                    <td>{event.number}</td>
                    <td><a id="showAccount" href="">{event.name}</a></td>                                        
                    <td>{event.created_by}</td>
                    <td>
                        <input 
                            id='account_create_date'
                            name='account_create_date'
                            type="datetime-local"
                            value="{event.modify_date.strftime('%Y-%m-%dT%H:%M')}" 
                            readonly">
                    </td>
                </tr>
            '''
          
        table += f'''
                </tbody>
            </table>
            
        '''
        return table 
    
   
    
    return checkRoleClearance(current_user.role, 'user', render_template
        (
            "view_eventlogs.html",
            user=current_user,
            dashUser=current_user,
            homeRoute='/',
            events=generateLogs(),
            
        ),
    )
@eventlog.route('/view_event')
@login_required
def view_event():

    eventid = request.args.get('number')
    curr_event = Event.query.filter_by(id=eventid).first()   
    curr_acct=Account.query.filter_by(number=curr_event.number).first()

    return render_template(
        "view_event.html",
        user=current_user,
        dashUser=current_user,
        homeRoute="/",  
        event = curr_event,
        account =curr_acct,
        back=url_for("eventlog.view_eventlogs"),         
        )
