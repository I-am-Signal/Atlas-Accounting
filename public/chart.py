from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Company, Credential, Account,Event
from . import db, formatMoney, unformatMoney
from .auth import login_required_with_password_expiration, checkRoleClearance
from .email import sendEmail, getEmailHTML
from datetime import datetime
from sqlalchemy import desc, asc

chart = Blueprint('chart', __name__)


@chart.route('/show_account', methods=['GET', 'POST'])
def show_account():
    account_number = request.args.get('number')
    
    """Loads the show_account page and handles its logic"""
    if request.method == 'GET':
        # once verify number method is made, replace this
        if account_number:
            account_number = int(account_number)
        accountInfo = Account.query.filter_by(number=account_number).first() if account_number else None
        statementTypes = [
            'Income Statement',
            'Balance Sheet', 
            'Retained Earnings Statement'
        ] # pull the actual statement types instead of these predetermined ones
        return checkRoleClearance(current_user.role, 'administrator', render_template(
                "account.html",
                user=current_user,
                dashUser=current_user,
                homeRoute='/',
                accountInfo=accountInfo if accountInfo else None,
                statementTypes=statementTypes if statementTypes else None,
                back=url_for('chart.view_accounts')
            )
        )
    
    
    if request.method == 'POST':
        account_name = request.form.get('account_name')
        account_number = request.form.get('account_number')
        account_desc = request.form.get('account_desc')
        normal_side = request.form.get('normal_side')
        account_category = request.form.get('account_category')
        account_subcat = request.form.get('account_subcat')
        order = request.form.get('order')
        statement = request.form.get('statement')
        comment = request.form.get('comment')
        
        if not account_number.isdigit():
            flash('Invalid account number. Only digits are allowed.', category='error')
            return redirect(url_for('chart.view_accounts'))

        #finish implementing other check requirements 2-5
        # account = Account.query.filter_by(account_number=account_number).first()
        # if account:
        #     flash(f'Account Number already exists', category='error')
       
        curr_account = Account.query.filter_by(number=account_number).first()
        # log current account info 
        new_event = Event(                 
                number=curr_account.number,
                name=curr_account.name,
                description=curr_account.description,
                normal_side=curr_account.normal_side, # check for valid normal side
                category=curr_account.category,
                subcategory=curr_account.subcategory,
                initial_balance=curr_account.initial_balance,
                balance=curr_account.balance,
                debit =curr_account.debit,
                credit=curr_account.credit,
                order=curr_account.order, # check if > 0, is int, and is not the same for the cat/subcat
                statement=curr_account.statement, # check if valid statement type
                comment=curr_account.comment,
                created_by=curr_account.created_by               
            )
        
        # else:
        if curr_account:
            debit = request.form.get('debit')
            credit = request.form.get('credit')
            balance = request.form.get('balance')

            
            
            curr_account.name = account_name
            curr_account.description = account_desc
            curr_account.normal_side = normal_side # check for valid normal side
            curr_account.category = account_category
            curr_account.subcategory = account_subcat
            curr_account.debit = unformatMoney(debit) # check for valid debit
            curr_account.credit = unformatMoney(credit) # check for valid credit
            curr_account.balance = unformatMoney(balance) # check for valid balance
            curr_account.order = order # check if > 0, is int, and is not the same for the cat/subcat
            curr_account.statement = statement # check if valid statement type
            curr_account.comment = comment

            
            db.session.add(new_event) 
            flash(f'Account #{curr_account.number}\'s information has been successfully updated.', category='success')
            
        else:
            initial_balance = request.form.get('initial_balance')

            new_account = Account(
                number=account_number, # check for unique account number
                name=account_name,
                description=account_desc,
                normal_side=normal_side, # check for valid normal side
                category=account_category,
                subcategory=account_subcat,
                initial_balance=unformatMoney(initial_balance), # check if valid
                balance=unformatMoney(initial_balance),
                order=order, # check if > 0, is int, and is not the same for the cat/subcat
                statement=statement, # check if valid statement type
                comment=comment,
                created_by=current_user.id,                
            )
           
            
            
            db.session.add(new_account)             
            flash(f'New Account created as Account #{new_account.number}!', category='success')            
        db.session.commit()
        return redirect(url_for('chart.view_accounts'))

@chart.route('/view_accounts', methods=['GET'])
@login_required
def view_accounts():
    
    # Used for when you mess in creating accounts in development
    # account number to delete duplicates of
    # accNumToDeleteDupes = 101
    # accounts = Account.query.filter_by(number=accNumToDeleteDupes).all()
    # for account in accounts[1:]:
    #     db.session.delete(account)
    #     db.session.commit()
        
    def generateAccounts():
        table = f'''
            <a href='{url_for('views.home')}'>Back</a> <br />
            <table class="userDisplay">
                <thead>
                    <tr>
                        <th>Account Number</th>
                        <th>Account Name</th>
                        <th>Category</th>
                        <th>Subcategory</th>
                        <th>Statement</th>
                        <th>Date Created</th>
                    </tr>
                </thead>
                <tbody>
        '''
        for account in Account.query.filter(Account.id).order_by(asc(Account.number)).all():
            table += f'''
                <tr>
                    <td>{account.number}</td>
                    <td><a id="showAccount" href="{url_for('chart.show_account', number=account.number)}">{account.name}</a></td>
                    <td>{account.category}</td>
                    <td>{account.subcategory}</td>
                    <td>{account.statement}</td>
                    <td>
                        <input 
                            id='account_create_date'
                            name='account_create_date'
                            type="datetime-local"
                            value="{account.create_date.strftime('%Y-%m-%dT%H:%M')}" 
                            readonly">
                    </td>
                </tr>
            '''
          
        table += f'''
                </tbody>
            </table>
            <a id="createAccount" href='{url_for('chart.show_account')}'>Create new Account</a>
        '''
        return table 
    
    return checkRoleClearance(current_user.role, 'administrator', render_template
        (
            "view_accounts.html",
            user=current_user,
            dashUser=current_user,
            homeRoute='/',
            accounts=generateAccounts()
        )
    )
