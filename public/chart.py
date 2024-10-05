from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Company, Credential,Account
from . import db, formatMoney
from .auth import login_required_with_password_expiration, checkRoleClearance
from .email import sendEmail, getEmailHTML
from datetime import datetime
from sqlalchemy import desc

chart = Blueprint('chart', __name__)


@chart.route('/create_account', methods=['GET', 'POST'])
def create_account():
    """Loads the create_account page and handles its logic"""
   

    if request.method == 'POST':
        account_name = request.form.get('account_name')
        account_number = request.form.get('account_number')
        account_desc = request.form.get('account_desc')
        normal_side = request.form.get('normal_side')
        account_category = request.form.get('account_category')
        account_subcat = request.form.get('account_subcat')
        initial_balance = request.form.get('initial_balance')
        debit = request.form.get('debit')
        credit = request.form.get('credit')
        order = request.form.get('order')
        statement = request.form.get('statement')
        comment = request.form.get('comment')
        
        #finish implementing other check requirements 2-5
        # account = Account.query.filter_by(account_number=account_number).first()
        # if account:
        #     flash(f'Account Number already exists', category='error')
       
        # else:
        new_account = Account(
            account_name=account_name,
            account_number=account_number,
            account_desc=account_desc,
            account_subcat=account_subcat,
            normal_side=normal_side,
            account_category=account_category,
            initial_balance=initial_balance,
            debit=debit,
            credit=credit,
            order=order,
            statement=statement,
            comment=comment
        )
        db.session.add(new_account)         
            
            
            #finish pulling account #
            #account = Account.query.filter_by(user_id=current_user).first()
                
        flash(f'New Account created as Account #{new_account.account_number}!', category='success')            
        db.session.commit()
        return redirect(url_for('chart.view_accounts'))

    return render_template("create_account.html",
                            user=current_user,
                              homeRoute='/',
                              back=url_for('chart.view_accounts'))

@chart.route('/view_accounts', methods=['GET', 'POST'])
@login_required
def view_accounts():
    def generateAccounts():
        table = f'''
            <a href='{url_for('views.home')}'>Back</a> <br />
            <div class="userDisplay">
                <p>Chart of Accounts Number Scheme:</p>
            </div>
            <table class="userDisplay">
                <thead>
                    <tr>
                        <th>Account ID</th>
                        <th>Account Name</th>
                        <th>Account #</th>
                        <th>Account Description</th>
                        <th>Balance</th>
                        <th>Statement</th>
                        <th>Date Created</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for account in Account.query.filter(Account.id).all():
            table += f'''
                <tr>
                    <td>{account.id}</td>
                    <td><a href="">{account.account_name}</a></td>
                    <td>{account.account_number}</td>
                    <td>{account.account_desc}</td>
                    <td>{account.balance}</td>
                    <td>{account.statement}</td>
                    <td>
                        <input 
                            id='account_create_date'
                            name='account_create_date'
                            type="datetime-local"
                            value="{account.create_date}" 
                            readonly">
                    </td>
                </tr>
            '''
          
        table += f'''
                </tbody>
            </table>
            <a href='{url_for('chart.create_account')}'>Create new Account</a>
        '''
        return table 
    
    return checkRoleClearance(current_user.role, 'administrator', render_template
        (
            "view_accounts.html",
            user=current_user,
            homeRoute='/',
            accounts=generateAccounts()
        )
    )
