from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Company, Credential, Account, Journal_Entry, Transaction,Event
from . import db, formatMoney, unformatMoney
from .auth import login_required_with_password_expiration, checkRoleClearance
from .email import sendEmail, getEmailHTML
from datetime import datetime, timedelta
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
        
        return checkRoleClearance(current_user.role, 'user', render_template(
                "account.html",
                access=True if current_user.role == 'user' else False,
                user=current_user,
                dashUser=current_user,
                homeRoute='/',
                accountInfo=accountInfo if accountInfo else None,
                statementTypes=statementTypes if statementTypes else None,
                back=url_for('chart.view_accounts')
            )
        )
    
    
    if request.method == 'POST':
        account_number_original = request.args.get('number')
        account_name = request.form.get('account_name')
        account_number = request.form.get('account_number')
        account_desc = request.form.get('account_desc')
        normal_side = request.form.get('normal_side')
        account_category = request.form.get('account_category')
        account_subcat = request.form.get('account_subcat')
        order = request.form.get('order')
        statement = request.form.get('statement')
        comment = request.form.get('comment')
        
        if not account_number.isdigit() or (account_number_original and not account_number_original.isdigit()):
            flash('Invalid account number. Only digits are allowed.', category='error')
            return redirect(url_for('chart.view_accounts'))

        #finish implementing other check requirements 2-5
        # account = Account.query.filter_by(account_number=account_number).first()
        # if account:
        #     flash(f'Account Number already exists', category='error')
       
        curr_account = Account.query.filter_by(number=account_number).first()
        # log current account info 
                   
            
        
        # else:
        if curr_account:
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

            
            
            curr_account.name = account_name
            curr_account.description = account_desc
            curr_account.normal_side = normal_side # check for valid normal side
            curr_account.category = account_category
            curr_account.subcategory = account_subcat
            curr_account.balance = unformatMoney(request.form.get('balance')) # check for valid balance
            curr_account.order = order # check if > 0, is int, and is not the same for the cat/subcat
            curr_account.statement = statement # check if valid statement type
            curr_account.comment = comment

            
            db.session.add(new_event) 
            flash(f'Account #{curr_account.number}\'s information has been successfully updated.', category='success')
            
        else:
            # check for duplicate number or name
            number  = Account.query.filter_by(number=account_number).first()
            name = Account.query.filter_by(name=account_name).first()
            
            # The account does not have both the name and number, but has either one of them
            if not(number and name) and (number or name):
                flash(
                    "New accounts cannot have the same name or number as previous accounts.",
                    category='error'
                )
                return redirect(url_for('chart.show_account'))
            
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
                company_id=current_user.company_id
            )
           
            
            
            db.session.add(new_account)             
            flash(f'New Account created as Account #{new_account.number}!', category='success')            
        db.session.commit()
        return redirect(url_for('chart.view_accounts'))


@chart.route("/deactivate", methods=["GET", "POST"])
@login_required
def deactivate():
    # when user_id check method is implemented, call it here instead of this
    ref_id = request.args.get("number")
    if not ref_id.isdigit():
        flash("Error: invalid reference number.", category='error')
        return redirect(url_for("chart.view_accounts"))
    ref_id = int(ref_id)
    
    account = Account.query.filter_by(number=ref_id).first()

    if request.method == "POST":
        # check account balance empty before deactivation
        if request.form.get("deactivate") != '' and account.balance != 0:
            flash('Accounts with a balance cannot be deactivated', category='error')
            return redirect(url_for('chart.view_accounts'))
        
        deactivate = request.form.get("deactivate") == 'True'
        active = account.is_activated
        flashMessage = f'Account number {account.number} was successfully '
        
        if deactivate != active:
            # early return as there is nothing to do
            flash('No changes occurred.', category='success')
            return redirect(url_for('chart.view_accounts'))
        
        account.is_activated = not active        
        db.session.commit()
        
        flashMessage += 'deactivated!' if deactivate and active else 'reactivated!'
        flash(flashMessage, category='success')
        return redirect(url_for("chart.view_accounts"))

    return checkRoleClearance(
        current_user.role,
        "administrator",
        render_template(
            "deactivate.html",
            user=current_user,
            dashUser=current_user,
            homeRoute="/",
            back=url_for("views.view_users"),
            account=account,
        ),
    )


from flask import request, url_for, render_template
from flask_login import login_required

@chart.route('/view_accounts', methods=['GET'])
@login_required
def view_accounts():
    # Used for when you mess in creating accounts in development
    # accNumToDeleteDupes = 101
    # accounts = Account.query.filter_by(number=accNumToDeleteDupes).all()
    # for account in accounts[1:]:
    #     db.session.delete(account)
    #     db.session.commit()
    
    # Used for when messing with account company ids to reset them for display
    # for account in Account.query.all():
    #     account.company_id = current_user.company_id
    #     account.is_activated = True
    #     db.session.commit()
    def generateAccounts():
        # Capture the account number and account name filter from the GET request parameters
        filter_number = request.args.get('filter_number', None)
        filter_name = request.args.get('filter_name', None)
        filter_category = request.args.get('filter_category', None)
        filter_subcategory = request.args.get('filter_subcategory', None)


        table = f'''
            <a href='{url_for('views.home')}'>Back</a> <br />
            
            <form method="get" action="{url_for('chart.view_accounts')}" style="margin-left:100px">
                <label for="filter_number"></label>
                <input type="text" id="filter_number" name="filter_number" placeholder="Enter Account Number" value="{filter_number if filter_number else ''}" />
                
                <label for="filter_name"></label>
                <input type="text" id="filter_name" name="filter_name" placeholder="Enter Account Name" value="{filter_name if filter_name else ''}" />
                
                <label for="filter_category"></label>
                <input type="text" id="filter_category" name="filter_category" placeholder="Enter Category Name" value="{filter_category if filter_category else ''}" />   
                
                <label for="filter_subcategory"></label>
                <input type="text" id="filter_subcategory" name="filter_subcategory" placeholder="Enter Subcategory Name" value="{filter_subcategory if filter_subcategory else ''}" />   
                
                    <button type="submit" style="background-color: #4CAF50; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer;">Filter</button>
               
                <a href="{url_for('chart.view_accounts')}" style="background-color: #AF4C4C; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer; font-weight:normal;>
                    <button type="button">Clear Filters</button>
                </a>
                
            </form>
            
            <table class="userDisplay">
                <thead>
                    <tr>
                        <th>Ledger</th>
                        <th>Account Number</th>
                        <th>Account Name</th>
                        <th>Category</th>
                        <th>Subcategory</th>
                        <th>Statement</th>
                        <th>Date Created</th>
                        <th>Active</th>
                    </tr>
                </thead>
                <tbody>
        '''
        
        query = Account.query.filter_by(company_id=current_user.company_id)

        if filter_number:
            query = query.filter(Account.number.like(f"%{filter_number}%"))
        
        if filter_name:
            query = query.filter(Account.name.like(f"%{filter_name}%"))
            
        if filter_category:
            query = query.filter(Account.category.like(f"%{filter_category}%"))
            
        if filter_subcategory:
            query = query.filter(Account.subcategory.like(f"%{filter_subcategory}%"))


        accounts = query.order_by(Account.is_activated.desc(), Account.number.asc()).all()

        for account in accounts:
            table += f'''
                <tr>
                    <td><a id="showLedger" href="{url_for('chart.ledger', number=account.number)}">Show Ledger</a></td>
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
                    <td>{account.is_activated}</td>
                </tr>
            '''

        table += f'''
                </tbody>
            </table>
            <a id="createAccount" href='{url_for('chart.show_account')}'>Create new Account</a>
        '''
        
        return table 
    
    # Render the template with the generated table
    return checkRoleClearance(current_user.role, 'user', render_template
        (
            "view_accounts.html",
            user=current_user,
            dashUser=current_user,
            homeRoute='/',
            accounts=generateAccounts()
        )
    )


@chart.route('/ledger', methods=['GET'])
@login_required
def ledger():
    
    # Used for when you mess in creating accounts in development
    # accNumToDeleteDupes = 101
    # accounts = Account.query.filter_by(number=accNumToDeleteDupes).all()
    # for account in accounts[1:]:
    #     db.session.delete(account)
    #     db.session.commit()
    
    # Used for when messing with account company ids to reset them for display
    # for account in Account.query.all():
    #     account.company_id = current_user.company_id
    #     db.session.commit()
    
    if request.method == 'GET':
        ref_id = request.args.get('number')
        if ref_id:
            if not ref_id.isdigit() or not db.session.query(Transaction).filter_by(account_number=int(ref_id)).all():
                flash(f'Invalid account reference number of {ref_id}', category='error')
                return redirect(url_for('views.home'))
            
        def generateLedger():
            table = f'''
                <a href='{url_for('views.home')}'>Back</a> <br />
                <table class="userDisplay">
                    <thead>
                        <tr>
                            <th>Reference Number</th>
                            <th>Accounts</th>
                            <th>Description</th>
                            <th>Date Created</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            '''
            
            def getAccountsInJournalEntry(referenceNumber):
                associatedAccounts = ''
                for account in db.session.query(Account).join(
                    Transaction, Transaction.account_number == Account.number
                ).filter(
                    Transaction.journal_entry_id == referenceNumber
                ).all():
                    associatedAccounts += f'{account.number} - {account.name}<br>'
                    
                return associatedAccounts
            
            # filter all journal entries for only those with an account with the ref_id if one is provided
            entries = db.session.query(Journal_Entry).join(
                Transaction, Journal_Entry.id == Transaction.journal_entry_id
            ).filter(
                Journal_Entry.company_id == current_user.company_id
            ).order_by(
                Journal_Entry.id.desc()
            ).all() if not ref_id else db.session.query(Journal_Entry).join(
                Transaction, Journal_Entry.id == Transaction.journal_entry_id
            ).filter(
                Journal_Entry.company_id == current_user.company_id,
                Transaction.account_number == ref_id
            ).order_by(
                Journal_Entry.id.desc()
            ).all()
                        
            for entry in entries:
                table += f'''
                    <tr>
                        <td><a href="{url_for('chart.journal_entry', id=entry.id)}">{entry.id}</a></td>
                        <td>{getAccountsInJournalEntry(entry.id)}</td>
                        <td>{entry.description}</td>
                        <td>
                            <input 
                                id='entry_create_date'
                                name='entry_create_date'
                                type="datetime-local"
                                value="{entry.create_date.strftime('%Y-%m-%dT%H:%M')}" 
                                readonly">
                        </td>
                        <td>{entry.status}</td>
                    </tr>
                '''
            
            table += f'''
                    </tbody>
                </table>
                <a href='{url_for('chart.journal_entry')}'>Create new journal entry</a>
            '''
            return table 
    
    return checkRoleClearance(current_user.role, 'administrator', render_template
        (
            "ledger.html",
            user=current_user,
            homeRoute='/',
            ledger=generateLedger()
        )
    )


@chart.route('/journal_entry', methods=['GET', 'POST'])
@login_required
def journal_entry():
    """
    GET: Provides the Journal Entry screen\n
    POST: Retrieves data from the screen, checks its safe, then saves it
    """
    # Used for when you mess in creating accounts in development
    # accNumToDeleteDupes = 101
    # accounts = Account.query.filter_by(number=accNumToDeleteDupes).all()
    # for account in accounts[1:]:
    #     db.session.delete(account)
    #     db.session.commit()
    
    # Used for when messing with account company ids to reset them for display
    # for account in Account.query.all():
    #     account.company_id = current_user.company_id
    #     db.session.commit()
    
    if request.method == 'POST':
        # this is currently just the 'user' view of it
        # admins (and potentially managers) need the ability to change status as well as delete
        
        ref_id = request.form.get('ref_id')
        status = request.form.get('status')
        entry_type = request.form.get('entry_type')
        description = request.form.get('description')
        
        accounts = []
        debits = []
        credits = []
        tos = []
        for accountNum in range(int(request.form.get('accountCount'))):
            accounts.append(request.form.get(f'account{accountNum}'))
            debits.append(unformatMoney(request.form.get(f'debit{accountNum}')))
            credits.append(unformatMoney(request.form.get(f'credit{accountNum}')))
            tos.append(request.form.get(f'to{accountNum}') == 'True')

        # check total debits and total credits are equivalent
        # does not currently check against account normal side
        if sum(debits) != sum(credits):
            flash('Total of debits was not equivalent to total of credits!', category='error')
            redirect(url_for('chart.journal_entry'))
        
        curr_journal_entry = Journal_Entry.query.filter_by(id=ref_id).first()
        
        if curr_journal_entry:
            transactions = Transaction.query.order_by(
                Transaction.id.asc()
            ).filter_by(journal_entry_id=ref_id).all()
            
            for accountNum in range(len(transactions)):
                transactions[accountNum].journal_entry_id = ref_id
                transactions[accountNum].side_for_transaction = 'Debit' if debits[accountNum] > 0 else 'Credit'
                transactions[accountNum].account_number = accounts[accountNum]
                transactions[accountNum].amount_changing = debits[accountNum] if debits[accountNum] > 0 else credits[accountNum]
                transactions[accountNum].to = tos[accountNum]
                transactions[accountNum].created_by = current_user.id
        
        # new entry to save
        else:
            entry = Journal_Entry(
                id = int(ref_id),
                status = status,
                company_id = current_user.company_id,
                entry_type = entry_type,
                description = description,
                created_by = current_user.id
            )
            db.session.add(entry)
            
            for accountNum in range(len(accounts)):
                transaction = Transaction(
                    journal_entry_id = entry.id,
                    side_for_transaction = 'Debit' if debits[accountNum] > 0 else 'Credit',
                    account_number = accounts[accountNum],
                    amount_changing = debits[accountNum] if debits[accountNum] > 0 else credits[accountNum],
                    to = tos[accountNum],
                    created_by = current_user.id
                )
                db.session.add(transaction)
        
        db.session.commit()
        flash(f'Journal Entry with Reference #: {curr_journal_entry.id if curr_journal_entry else entry.id} has been saved successfully!', category='success')
        return redirect(url_for('chart.ledger'))
        

    if request.method == 'GET':
        ref_id = request.args.get('id')
        if ref_id:
            try:
                ref_id = int(ref_id)
            except:
                flash('Invalid reference number.', category='error')
                return redirect(url_for('views.home'))
        
        def generateJournalEntry(ref_id = None):
            curr_journal_entry = None
            newJournalEntry = False
            if None == ref_id:
                newJournalEntry = True
                try:
                    ref_id = Journal_Entry.query.order_by(Journal_Entry.id.desc()).first().id + 1
                except:
                    ref_id = 1
            else:
                curr_journal_entry = Journal_Entry.query.filter_by(id=ref_id).first()
            
            # This renders the contents of above and the top of the table
            table = f'''
                <input type='hidden' value='{ref_id}' name='ref_id' id='ref_id'>
                <input type='hidden' value='{'New' if newJournalEntry else curr_journal_entry.status} name='status' id='status'>
                <p>
                    <a href='{url_for('chart.ledger')}'>Back</a>&ensp;
                    Reference&nbsp;#:&ensp;<strong>{ref_id}</strong>&ensp;
                    Date:&nbsp;<input
                            id='entry_create_date'
                            name='entry_create_date'
                            type="datetime-local"
                            value="{(datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M')}" 
                            readonly">&ensp;
                    Status:&nbsp;{'New' if newJournalEntry else Journal_Entry.query.filter_by(
                            id=ref_id
                        ).first().status}&ensp;
                    Entry&nbsp;Type:&nbsp;<select id="entry_type" name="entry_type">
                        <option value="Opening" {'selected' if curr_journal_entry and curr_journal_entry.entry_type == 'Opening' else ''}>Opening</option>
                        <option value="Transfer" {'selected' if curr_journal_entry and curr_journal_entry.entry_type == 'Transfer' else ''}>Transfer</option>
                        <option value="Closing" {'selected' if curr_journal_entry and curr_journal_entry.entry_type == 'Closing' else ''}>Closing</option>
                        <option value="Adjusting" {'selected' if curr_journal_entry and curr_journal_entry.entry_type == 'Adjusting' else ''}>Adjusting</option>
                        <option value="Compound" {'selected' if curr_journal_entry and curr_journal_entry.entry_type == 'Compound' else ''}>Compound</option>
                        <option value="Reversing" {'selected' if curr_journal_entry and curr_journal_entry.entry_type == 'Reversing' else ''}>Reversing</option>
                    </select>
                    <label for='description'>Description&nbsp;of&nbsp;Transaction:</label>
                    <textarea name="description" id="description">{ curr_journal_entry.description if curr_journal_entry else '' }</textarea>

                </p>
                <table class="userDisplay">
                    <thead>
                        <tr>
                            <th>Account</th>
                            <th>To</th>
                            <th>Debit</th>
                            <th>Credit</th>
                        </tr>
                    </thead>
                    <tbody>
            '''
            
            # obtains the accounts and transactions of the current entry, if there is one
            accounts_of_entry = []
            transactions_of_entry = []
            for account, transaction in db.session.query(Account, Transaction).join(
                    Transaction, Transaction.account_number == Account.number
                ).filter(
                    Transaction.journal_entry_id == ref_id
                ).all():
                accounts_of_entry.append(account)
                transactions_of_entry.append(transaction)
            
            def selectElementWithAccounts(id):
                accounts = Account.query.filter_by(company_id=current_user.company_id).all()
                select = f'''
                <select id='account{id}' name='account{id}'>
                    <option value=''>-- Select and Account --</options>
                '''
                for account in accounts:
                    select += f'''<option value="{account.number}" {
                        'selected' if accounts_of_entry and accounts_of_entry[id].number == account.number else ''
                    }>{account.number} - {account.name}: {account.normal_side}</option>'''
                
                return select + '</select>'
            
            for i in range(2):
                table += f'''
                    <tr>
                        <td>{selectElementWithAccounts(i)}</td>
                        <td><select id='to{i}' name='to{i}'>
                            <option value='True' {'selected' if transactions_of_entry and transactions_of_entry[i].to == True else ''}>True</option>
                            <option value='False' {'selected' if transactions_of_entry and not (transactions_of_entry[i].to == True) else ''}>False</option>
                        </select>
                        <td><input id='debit{i}' name='debit{i}' value='{
                            transactions_of_entry[i].amount_changing if transactions_of_entry and transactions_of_entry[i].side_for_transaction == 'Debit' else 0
                        }'></td>
                        <td><input id='credit{i}' name='credit{i}' value='{
                            transactions_of_entry[i].amount_changing if transactions_of_entry and transactions_of_entry[i].side_for_transaction == 'Credit' else 0
                        }'></td>
                    </tr>
                '''
            
            table += f'''
                    </tbody>
                </table>
                <div class='form-buttons'>
                <button type=submit>Submit for Approval</button>
                    <button type='button' onclick="window.location.href='{ url_for('chart.ledger')}'">Cancel</button>
                </div>
                <input type='hidden' value='2' name='accountCount' id='accountCount'>
            '''
            return table 
    
    return checkRoleClearance(current_user.role, 'user', render_template
        (
            "journal_entry.html",
            user=current_user,
            dashUser=current_user,
            homeRoute='/',
            entry=generateJournalEntry(ref_id)
        )
    )