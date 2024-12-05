from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import (
    Account,
    Journal_Entry,
    Transaction,
    Event,
)
from . import db, formatMoney, unformatMoney
from .auth import checkRoleClearance
from .email import getEmailHTML, sendEmailToAllUsersWithRole
from datetime import datetime, timedelta
from .preload import load_accounts

chart = Blueprint("chart", __name__)


@chart.route("/show_account", methods=["GET", "POST"])
def show_account():
    account_number = request.args.get("number")

    """Loads the show_account page and handles its logic"""
    if request.method == "GET":
        if account_number:
            account_number = int(account_number)
        accountInfo = (
            Account.query.filter_by(
                number=account_number,
                company_id=current_user.company_id,
            ).first()
            if account_number
            else None
        )
        statementTypes = [
            "Income Statement",
            "Balance Sheet",
            "Retained Earnings Statement",
            "Statement of Cash Flows",
            "Statement of Stockholder Equity",
        ]

        return checkRoleClearance(
            current_user.role,
            "user",
            render_template(
                "account.html",
                access=True if current_user.role == "administrator" or current_user.role == "user" else False,
                user=current_user,
                dashUser=current_user.role,
                homeRoute="/",
                accountInfo=accountInfo if accountInfo else None,
                statementTypes=statementTypes if statementTypes else None,
                back=url_for("chart.view_accounts"),
            ),
        )

    if request.method == "POST":
        account_number_original = request.args.get("number")
        account_name = request.form.get("account_name")
        account_number = request.form.get("account_number")
        account_desc = request.form.get("account_desc")
        normal_side = request.form.get("normal_side")
        account_category = request.form.get("account_category")
        account_subcat = request.form.get("account_subcat")
        order = request.form.get("order")
        statement = request.form.get("statement")
        comment = request.form.get("comment")

        if not account_number.isdigit() or (
            account_number_original and not account_number_original.isdigit()
        ):
            flash("Invalid account number. Only digits are allowed.", category="error")
            return redirect(url_for("chart.view_accounts"))

        curr_account = Account.query.filter_by(number=account_number).first()
        if curr_account:
            # log current account info
            new_event = Event(
                is_new=False,
                number=curr_account.number,
                name=curr_account.name,
                description=curr_account.description,
                normal_side=curr_account.normal_side,  # check for valid normal side
                category=curr_account.category,
                subcategory=curr_account.subcategory,
                initial_balance=curr_account.initial_balance,
                balance=curr_account.balance,
                debit=curr_account.debit,
                credit=curr_account.credit,
                order=curr_account.order,  # check if > 0, is int, and is not the same for the cat/subcat
                statement=curr_account.statement,  # check if valid statement type
                comment=curr_account.comment,
                created_by=curr_account.created_by,
            )

            curr_account.name = account_name
            curr_account.description = account_desc
            curr_account.normal_side = normal_side  # check for valid normal side
            curr_account.category = account_category
            curr_account.subcategory = account_subcat
            curr_account.balance = unformatMoney(
                request.form.get("balance")
            )  # check for valid balance
            curr_account.order = (
                order  # check if > 0, is int, and is not the same for the cat/subcat
            )
            curr_account.statement = statement  # check if valid statement type
            curr_account.comment = comment

            db.session.add(new_event)
            flash(
                f"Account #{curr_account.number}'s information has been successfully updated.",
                category="success",
            )

        else:
            # check for duplicate number or name
            number = Account.query.filter_by(number=account_number).first()
            name = Account.query.filter_by(name=account_name).first()

            # The account does not have both the name and number, but has either one of them
            if not (number and name) and (number or name):
                flash(
                    "New accounts cannot have the same name or number as previous accounts.",
                    category="error",
                )
                return redirect(url_for("chart.show_account"))

            initial_balance = request.form.get("initial_balance")

            new_account = Account(
                number=account_number,  # check for unique account number
                name=account_name,
                description=account_desc,
                normal_side=normal_side,  # check for valid normal side
                category=account_category,
                subcategory=account_subcat,
                initial_balance=unformatMoney(initial_balance),  # check if valid
                balance=unformatMoney(initial_balance),
                order=order,  # check if > 0, is int, and is not the same for the cat/subcat
                statement=statement,  # check if valid statement type
                comment=comment,
                created_by=current_user.id,
                company_id=current_user.company_id,
            )

            new_event = Event(
                is_new=True,
                number=new_account.number,
                name=new_account.name,
                description=new_account.description,
                normal_side=new_account.normal_side,  # check for valid normal side
                category=new_account.category,
                subcategory=new_account.subcategory,
                initial_balance=new_account.initial_balance,
                balance=new_account.balance,
                debit=new_account.debit,
                credit=new_account.credit,
                order=new_account.order,  # check if > 0, is int, and is not the same for the cat/subcat
                statement=new_account.statement,  # check if valid statement type
                comment=new_account.comment,
                created_by=new_account.created_by,
            )

            db.session.add(new_account)
            db.session.add(new_event)
            flash(
                f"New Account created as Account #{new_account.number}!",
                category="success",
            )
        db.session.commit()
        return redirect(url_for("chart.view_accounts"))


@chart.route("/deactivate", methods=["GET", "POST"])
@login_required
def deactivate():
    ref_id = request.args.get("number")
    if not ref_id.isdigit():
        flash("Error: invalid reference number.", category="error")
        return redirect(url_for("chart.view_accounts"))
    ref_id = int(ref_id)

    account = Account.query.filter_by(number=ref_id).first()

    if request.method == "POST":
        # check account balance empty before deactivation
        if request.form.get("deactivate") != "" and account.balance != 0:
            flash("Accounts with a balance cannot be deactivated", category="error")
            return redirect(url_for("chart.view_accounts"))

        deactivate = request.form.get("deactivate") == "True"
        active = account.is_activated
        flashMessage = f"Account number {account.number} was successfully "

        if deactivate != active:
            # early return as there is nothing to do
            flash("No changes occurred.", category="success")
            return redirect(url_for("chart.view_accounts"))

        account.is_activated = not active
        db.session.commit()

        flashMessage += "deactivated!" if deactivate and active else "reactivated!"
        flash(flashMessage, category="success")
        return redirect(url_for("chart.view_accounts"))

    return checkRoleClearance(
        current_user.role,
        "administrator",
        render_template(
            "deactivate.html",
            user=current_user,
            dashUser=current_user.role,
            homeRoute="/",
            back=url_for("chart.show_account", number=ref_id),
            account=account,
        ),
    )


from flask import request, url_for, render_template
from flask_login import login_required


@chart.route("/view_accounts", methods=["GET"])
@login_required
def view_accounts():
    # change the var in the preload file to True to load the accounts
    load_accounts() 
    def generateAccounts():
        # Capture the account number and account name filter from the GET request parameters
        filter_number = request.args.get("filter_number", None)
        filter_name = request.args.get("filter_name", None)
        filter_category = request.args.get("filter_category", None)
        filter_subcategory = request.args.get("filter_subcategory", None)
        filter_statement = request.args.get("filter_statement", None)
        filter_true = request.args.get("filter_true", None)

        table = f"""
            <a href='{url_for('views.home')}'>Back</a> <br />
            
            <form method="get" action="{url_for('chart.view_accounts')}" style="margin-left:100px">
                <label for="filter_number"></label>
                <input type="text" id="filter_number" name="filter_number" placeholder="Enter Account Number" value="{filter_number if filter_number else ''}" />
                
                <label for="filter_name"></label>
                <input type="text" id="filter_name" name="filter_name" placeholder="Enter Account Name" value="{filter_name if filter_name else ''}" />
                
                <label for="filter_category"></label>
                <input type="text" id="filter_category" name="filter_category" placeholder="Enter Category Name" value="{filter_category if filter_category else ''}" />   
                
                <label for="filter_subcategory"></label>
                <input type="text" id="filter_subcategory" name="filter_subcategory" placeholder="Enter Subcategory" value="{filter_subcategory if filter_subcategory else ''}" />  
                
                <label for="filter_statement"></label>
                <select id="filter_statement" name="filter_statement">
                    <option value="">All Statements</option>
                    <option value="Retained Earnings Statement" {'selected' if filter_statement == 'Retained Earnings Statement' else ''}>Retained Earnings Statement</option>
                    <option value="Balance Sheet" {'selected' if filter_statement == 'Balance Sheet' else ''}>Balance Sheet</option>
                    <option value="Income Statement" {'selected' if filter_statement == 'Income Statement' else ''}>Income Statement</option>
                    <option value="Statement of Cash Flows" {'selected' if filter_statement == 'Statement of Cash Flows' else ''}>Statement of Cash Flows</option>
                    <option value="Statement of Stockholder Equity" {'selected' if filter_statement == 'Statement of Stockholder Equity' else ''}>Statement of Stockholder Equity</option>
                </select>  
                
                <label for="filter_true"></label>
                <select id="filter_true" name="filter_true">
                    <option value="">All Activations</option>
                    <option value="True" {'selected' if filter_true == 'True' else ''}>True</option>
                    <option value="False" {'selected' if filter_true == 'False' else ''}>False</option>
                </select>  
                
                <button type="submit" class="filterBy">Filter</button>
               
                <a href="{url_for('chart.view_accounts')}">
                    <button type="button" class="clearFilters">Clear Filters</button>
                </a>
                
            </form>
            
            <table class="userDisplay">
                <thead>
                    <tr>
                        <th id="showLedger" >Ledger</th>
                        <th>Account Number</th>
                        <th id="showAccount">Account Name</th>
                        <th>Category</th>
                        <th>Subcategory</th>
                        <th>Statement</th>
                        <th>Date Created</th>
                        <th>Active</th>
                    </tr>
                </thead>
                <tbody>
        """

        query = Account.query.filter_by(company_id=current_user.company_id)

        if filter_number:
            query = query.filter(Account.number.like(f"%{filter_number}%"))

        if filter_name:
            query = query.filter(Account.name.like(f"%{filter_name}%"))

        if filter_category:
            query = query.filter(Account.category.like(f"%{filter_category}%"))

        if filter_subcategory:
            query = query.filter(Account.subcategory.like(f"%{filter_subcategory}%"))

        if filter_statement and filter_statement != "All":
            query = query.filter(Account.statement == filter_statement)

        if filter_true:
            active = True if filter_true == "True" else False
            query = query.filter(Account.is_activated == active)

        accounts = query.order_by(
            Account.is_activated.desc(), Account.number.asc()
        ).all()

        for account in accounts:
            table += f"""
                <tr>
                    <td><a href="{url_for('chart.ledger', number=account.number)}">Show Ledger</a></td>
                    <td>{account.number}</td>
                    <td><a  href="{url_for('chart.show_account', number=account.number)}">{account.name}</a></td>
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
            """

        table += f"""
                </tbody>
            </table>
            <a id="createAccount" href='{url_for('chart.show_account')}'>Create new Account</a>&emsp;
            <a id="createAccount" href='{url_for('email.send')}'>Send an Email</a>
        """

        return table

    # Render the template with the generated table
    return checkRoleClearance(
        current_user.role,
        "user",
        render_template(
            "view_accounts.html",
            user=current_user,
            dashUser=current_user.role,
            homeRoute="/",
            accounts=generateAccounts(),
        ),
    )


@chart.route("/ledger", methods=["GET"])
@login_required
def ledger():
    if request.method == "GET":
        ref_id = request.args.get("number", None)
        filter_description = request.args.get("filter_description", None)
        filter_reference_number = request.args.get("filter_reference_number", None)
        filter_account = request.args.get("filter_account", None)
        filter_debit = request.args.get("filter_debit", None)
        filter_credit = request.args.get("filter_credit", None)
        filter_status = request.args.get("filter_status", None)
        filter_type = request.args.get("filter_type", None)
        filter_comment = request.args.get("filter_comment", None)
        filter_date = request.args.get("filter_date", None)

        if ref_id:
            if not ref_id.isdigit():
                flash(f"Invalid account reference number of {ref_id}", category="error")
                return redirect(url_for("views.home"))
            if (
                not db.session.query(Transaction)
                .filter_by(account_number=int(ref_id))
                .all()
            ):
                flash(
                    f"No journal entries for account number {ref_id}!", category="error"
                )

        def generateLedger():
            table = f"""
                <a href='{url_for('views.home')}'>Back</a> <br />
                <form method="get" action="{url_for('chart.ledger')}">
                    <input type="date" id="filter_date" name="filter_date" value="{filter_date if filter_date else ''}" />

                    <input type="text" id="filter_reference_number" name="filter_reference_number" placeholder="Reference No." value="{filter_reference_number if filter_reference_number else ''}" />   
                    
                    <input type="text" id="filter_account" name="filter_account" placeholder="Account Number" value="{filter_account if filter_account else ''}" />
                    
                    <input type="text" id="filter_description" name="filter_description" placeholder="Description" value="{filter_description if filter_description else ''}" />

                    <input type="text" id="filter_debit" name="filter_debit" placeholder="Debit" value="{filter_debit if filter_debit else ''}" />
                                        
                    <input type="text" id="filter_credit" name="filter_credit" placeholder="Credit" value="{filter_credit if filter_credit else ''}" />
                    
                    <select id="filter_type" name="filter_type">
                        <option value="">-- Select Entry Type --</option>
                        <option value="Opening" {'selected' if filter_status == 'Opening' else ''}>Opening</option>
                        <option value="Transfer" {'selected' if filter_status == 'Transfer' else ''}>Transfer</option>
                        <option value="Closing" {'selected' if filter_status == 'Closing' else ''}>Closing</option>
                        <option value="Adjusting" {'selected' if filter_status == 'Adjusting' else ''}>Adjusting</option>
                        <option value="Compound" {'selected' if filter_status == 'Compound' else ''}>Compound</option>
                        <option value="Reversing" {'selected' if filter_status == 'Reversing' else ''}>Reversing</option>
                    </select>

                    <select id="filter_status" name="filter_status">
                        <option value="">-- Select Status (All) --</option>
                        <option value="Pending" {'selected' if filter_status == 'Pending' else ''}>Pending</option>
                        <option value="Approved" {'selected' if filter_status == 'Approved' else ''}>Approved</option>
                        <option value="Rejected" {'selected' if filter_status == 'Rejected' else ''}>Rejected</option>
                    </select>
                    
                    <input type="text" id="filter_comment" name="filter_comment" placeholder="Comment" value="{filter_comment if filter_comment else ''}" />

                    <button type="submit" class="filterBy">Filter</button>
                    
                    <a href="{url_for('chart.ledger')}">
                        <button type="button" class="clearFilters">Clear Filters</button>
                    </a>
                </form>

                <table class="userDisplay">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Reference Number</th>
                            <th>Accounts</th>
                            <th>Type</th>
                            <th>Debit</th>
                            <th>Credit</th>
                            <th>Balance</th>
                            <th>Status</th>
                            <th>Reject Comment</th>
                        </tr>
                    </thead>
                    <tbody>
            """

            def getAccountsInJournalEntry(referenceNumber):
                associatedAccounts = ""
                for account in (
                    db.session.query(Account)
                    .join(Transaction, Transaction.account_number == Account.number)
                    .filter(Transaction.journal_entry_id == referenceNumber)
                    .all()
                ):
                    associatedAccounts += f"{account.number} - {account.name}<br>"
                return associatedAccounts

            query = (
                db.session.query(Journal_Entry)
                .join(Transaction, Journal_Entry.id == Transaction.journal_entry_id)
                .filter(Journal_Entry.company_id == current_user.company_id)
            )
            if filter_reference_number:
                query = query.filter(
                    Journal_Entry.id.like(f"%{filter_reference_number}%")
                )

            if filter_description:
                query = query.filter(
                    Journal_Entry.description.like(f"%{filter_description}%")
                )

            if filter_account:
                query = query.filter(
                    Transaction.account_number.like(f"%{filter_account}%")
                )

            if filter_debit:
                query = query.filter(
                    Transaction.amount_changing.like(f"%{filter_debit}%")
                )

            if filter_credit:
                query = query.filter(
                    Transaction.amount_changing.like(f"%{filter_credit}%")
                )

            if filter_status:
                query = query.filter(Journal_Entry.status.like(f"%{filter_status}%"))

            if filter_type:
                query = query.filter(Journal_Entry.entry_type.like(f"%{filter_type}%"))

            if filter_comment:
                query = query.filter(Journal_Entry.comment.like(f"%{filter_comment}%"))

            if filter_date:
                query = query.filter(
                    db.func.date(Journal_Entry.create_date) == filter_date
                )

            entries = query.order_by(Journal_Entry.id.desc()).all()
            # Track the running balance
            balance = 0.0

            for entry in entries:
                # Calculate total debit and credit for the entry
                debit = sum(
                    t.amount_changing
                    for t in entry.transactions.filter_by(side_for_transaction="Debit")
                )
                credit = sum(
                    t.amount_changing
                    for t in entry.transactions.filter_by(side_for_transaction="Credit")
                )
                # Update the running balance
                balance += debit - credit

                # Add row to the table
                table += f"""
                    <tr>
                        <td>{entry.create_date.strftime('%Y-%m-%d')}</td>
                        <td><a href="{url_for('chart.journal_entry', id=entry.id)}">{entry.id}</a></td>
                        <td>{getAccountsInJournalEntry(entry.id)}</td>
                        <td>{entry.entry_type}</td>
                        <td>${formatMoney(debit)}</td>
                        <td>${formatMoney(credit)}</td>
                        <td>${formatMoney(balance)}</td>
                        <td>{entry.status}</td>
                        <td>{entry.comment if entry.comment else ""}</td>
                    </tr>
                """

            table += f"""
                    </tbody>
                </table>
                <a href='{url_for('chart.journal_entry')}'>Create new journal entry</a>
            """
            return table

    return checkRoleClearance(
        current_user.role,
        "user",
        render_template(
            "ledger.html",
            user=current_user,
            dashUser=current_user.role,
            homeRoute="/",
            ledger=generateLedger(),
        ),
    )


# This will create a directory named "uploads" to store the files uplaoded, if it doesn't already exist it will create one
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "csv", "jpg", "jpeg", "png"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@chart.route("/journal_entry", methods=["GET", "POST"])
@login_required
def journal_entry():
    """
    GET: Provides the Journal Entry screen\n
    POST: Retrieves data from the screen, checks its safe, then saves it
    """
    # this sets how many accounts there is to select in a journal entry
    numOfAccounts = Account.query.filter_by(company_id=current_user.company_id).count()

    if request.method == "POST":
        # this is currently just the 'user' view of it
        # admins (and potentially managers) need the ability to change status as well as delete

        ref_id = request.form.get("ref_id")
        status = request.form.get("status")
        entry_type = request.form.get("entry_type")
        description = request.form.get("description")
        comment = request.form.get("comment")

        accounts = []
        debits = []
        credits = []
        tos = []

        accounts_of_entry = []
        transactions_of_entry = []
        for account, transaction in (
            db.session.query(Account, Transaction)
            .join(Transaction, Transaction.account_number == Account.number)
            .filter(Transaction.journal_entry_id == ref_id)
            .all()
        ):
            accounts_of_entry.append(account)
            transactions_of_entry.append(transaction)

        cycleCount = (
            len(accounts_of_entry) if len(accounts_of_entry) > 0 else numOfAccounts
        )

        for accountNum in range(cycleCount):
            accounts.append(request.form.get(f"account{accountNum}"))
            debits.append(unformatMoney(request.form.get(f"debit{accountNum}")))
            credits.append(unformatMoney(request.form.get(f"credit{accountNum}")))
            tos.append(request.form.get(f"to{accountNum}") == "True")

        # Handle the file upload (do not require a file, but offer it as an option)
        file = request.files.get("attachment")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

        curr_journal_entry = Journal_Entry.query.filter_by(id=ref_id).first()

        # check total debits and total credits are equivalent
        if sum(debits) != sum(credits):
            flash(
                "Total of debits was not equivalent to total of credits!",
                category="error",
            )
            if curr_journal_entry:
                return redirect(
                    url_for("chart.journal_entry", id=curr_journal_entry.id)
                )
            return redirect(url_for("chart.journal_entry"))

        # check the normal side of the accounts corresponds with the entries
        error_return = False
        toCount = 0
        for i in range(len(accounts)):
            if accounts[i] != "":
                acc_to_evalute = Account.query.filter_by(number=accounts[i]).first()
                if (
                    acc_to_evalute.normal_side == "Debit"
                    and credits[i] != 0
                    or acc_to_evalute.normal_side == "Credit"
                    and debits[i] != 0
                ):
                    flash(
                        f"Invalid placement of credits and debits with respect to account #{i}!",
                        category="error",
                    )
                    error_return = True
                if tos[i] == True:
                    toCount += 1

            # check each account appears only once
            for j in range(1, len(accounts)):
                j += i
                if j >= len(accounts):
                    break
                if (
                    accounts[i] == accounts[j]
                    and accounts[j] != ""
                    and error_return == False
                ):
                    flash(
                        "Each account can only appear in a journal entry once!",
                        category="error",
                    )
                    error_return = True

        # check the to's are valid
        if tos[0] == True:
            flash(f"First account must always be a 'FROM' account!", category="error")
            error_return = True
        if toCount == len(tos):
            flash("Must have at least one 'FROM' account!", category="error")
            error_return = True

        if error_return == True:
            return (
                redirect(url_for("chart.journal_entry", id=curr_journal_entry.id))
                if curr_journal_entry
                else redirect(url_for("chart.journal_entry"))
            )

        if curr_journal_entry:
            transactions = (
                Transaction.query.order_by(Transaction.id.asc())
                .filter_by(journal_entry_id=ref_id)
                .all()
            )

            for accountNum in range(len(transactions)):
                transactions[accountNum].journal_entry_id = ref_id
                transactions[accountNum].side_for_transaction = (
                    "Debit" if debits[accountNum] > 0 else "Credit"
                )
                transactions[accountNum].account_number = accounts[accountNum]
                transactions[accountNum].amount_changing = (
                    debits[accountNum]
                    if debits[accountNum] > 0
                    else credits[accountNum]
                )
                transactions[accountNum].to = tos[accountNum]
                transactions[accountNum].created_by = current_user.id

        # new entry to save
        else:
            entry = Journal_Entry(
                id=int(ref_id),
                status=status,
                company_id=current_user.company_id,
                entry_type=entry_type,
                description=description,
                created_by=current_user.id,
                comment=comment,
            )
            db.session.add(entry)

            for accountNum in range(len(accounts)):
                transaction = Transaction(
                    journal_entry_id=entry.id,
                    side_for_transaction=(
                        "Debit" if debits[accountNum] > 0 else "Credit"
                    ),
                    account_number=accounts[accountNum],
                    amount_changing=(
                        debits[accountNum]
                        if debits[accountNum] > 0
                        else credits[accountNum]
                    ),
                    to=tos[accountNum],
                    created_by=current_user.id,
                )
                db.session.add(transaction)

            sendEmailToAllUsersWithRole(
                current_user.company_id,
                "manager",
                "New Journal Entry",
                getEmailHTML(
                    entry_id=entry.id,
                    pathToHTML="email_templates/new_journal_entry.html",
                ),
            )

        db.session.commit()
        flash(
            f"Journal Entry with Reference #: {curr_journal_entry.id if curr_journal_entry else entry.id} has been saved successfully!",
            category="success",
        )
        return redirect(url_for("chart.ledger"))

    if request.method == "GET":
        ref_id = request.args.get("id")
        if ref_id:
            try:
                ref_id = int(ref_id)
            except:
                flash("Invalid reference number.", category="error")
                return redirect(url_for("views.home"))

        def generateJournalEntry(ref_id=None):
            curr_journal_entry = None
            newJournalEntry = False
            if None == ref_id:
                newJournalEntry = True
                try:  # set ref_id to the last JE added plus one
                    ref_id = (
                        Journal_Entry.query.order_by(Journal_Entry.id.desc()).first().id
                        + 1
                    )
                except:  # if no JEs, ref_id is the first one
                    ref_id = 1
            else:  # get existing JE if there is one
                curr_journal_entry = Journal_Entry.query.filter_by(id=ref_id).first()

            # This renders the contents of above and the top of the table
            table = f"""
                <input type='hidden' value='{ref_id}' name='ref_id' id='ref_id'>
                <input type='hidden' value='{'New' if newJournalEntry else curr_journal_entry.status} name='status' id='status'>
                <input type='hidden' value='{numOfAccounts}' name='numOfAccounts' id='numOfAccounts'>
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
                    <label for='description' style="font-weight: bold">Description&nbsp;of&nbsp;Transaction:</label>
                    <textarea name="description" id="description" class="description-textarea">{ curr_journal_entry.description if curr_journal_entry else '' }</textarea>

                    <p>
                <label for="attachment" style="font-weight: bold">Attach File:</label>
                <input type="file" id="attachment" name="attachment" accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.jpg,.jpeg,.png" hidden>
                <button type="button" class="custom-file-button" onclick="document.getElementById('attachment').click()">Choose File</button>
                <span id="file-selected">No file chosen</span>
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
            """

            # obtains the accounts and transactions of the current entry, if there is one
            accounts_of_entry = []
            transactions_of_entry = []
            for account, transaction in (
                db.session.query(Account, Transaction)
                .join(Transaction, Transaction.account_number == Account.number)
                .filter(Transaction.journal_entry_id == ref_id)
                .all()
            ):
                accounts_of_entry.append(account)
                transactions_of_entry.append(transaction)

            def selectElementWithAccounts(index):
                accounts = Account.query.filter_by(
                    company_id=current_user.company_id
                ).all()
                select = f"""
                <select id='account{index}' name='account{index}'>
                    <option value=''>-- Select and Account --</options>
                """
                for account in accounts:
                    length = len(accounts_of_entry)
                    curr_account_is_selected = False
                    if length > index and length > 0:
                        curr_account_is_selected = (
                            accounts_of_entry[index].number == account.number
                        )
                    select += f"""<option value="{account.number}" {
                        'selected' if curr_account_is_selected else ''
                    }>{account.number} - {account.name}: {account.category}</option>"""

                return select + "</select>"

            # take into account if this is displaying an existing JE or if displaying new
            cycleCount = (
                len(accounts_of_entry) if len(accounts_of_entry) > 0 else numOfAccounts
            )

            for i in range(cycleCount):
                table += f"""
                    <tr>
                        <td>{selectElementWithAccounts(i)}</td>
                        <td><select id='to{i}' name='to{i}'>
                            <option value='True' {'selected' if len(transactions_of_entry) > i and transactions_of_entry[i].to == True else ''}>True</option>
                            <option value='False' {'selected' if len(transactions_of_entry) > i and not (transactions_of_entry[i].to == True) else ''}>False</option>
                        </select>
                        <td><input id='debit{i}' name='debit{i}' value='{
                            transactions_of_entry[i].amount_changing if len(transactions_of_entry) > i and transactions_of_entry[i].side_for_transaction == 'Debit' else 0
                        }'></td>
                        <td><input id='credit{i}' name='credit{i}' value='{
                            transactions_of_entry[i].amount_changing if len(transactions_of_entry) > i and transactions_of_entry[i].side_for_transaction == 'Credit' else 0
                        }'></td>
                    </tr>
                """

            table += f"""
                    </tbody>
                </table>
                <div class='form-buttons'>
                <button type=submit>Submit for Approval</button>             
                <button type='button' onclick="window.location.href='{ url_for('chart.approve_reject',id=ref_id)}'">Approve</button>
                <button type='button' onclick="window.location.href='{ url_for('chart.ledger')}'">Cancel</button>                
                </div>
                <input type='hidden' value='2' name='accountCount' id='accountCount'>
            """
            return table

    # verify that at least 2 account exist to create a journal entry
    if numOfAccounts < 2:
        flash(
            "At least 2 accounts must exist to complete a journal entry!",
            category="errror",
        )
        return redirect(url_for("chart.ledger"))

    return checkRoleClearance(
        current_user.role,
        "user",
        render_template(
            "journal_entry.html",
            user=current_user,
            dashUser=current_user.role,
            homeRoute="/",
            helpRoute="/help",
            entry=generateJournalEntry(ref_id),
        ),
    )


@chart.route("/approve_reject", methods=["GET", "POST"])
@login_required
def approve_reject():

    # when user_id check method is implemented, call it here instead of this
    ref_id = request.args.get("id")
    if not ref_id.isdigit():
        flash("Error: invalid reference number.", category="error")
        return redirect(url_for("chart.view_accounts"))
    ref_id = int(ref_id)

    # Fetch the journal entry from the database
    curr_journal = Journal_Entry.query.filter_by(id=ref_id).first()
    
    if request.method == "POST":

        arp = request.form.get("arp")
        comment = request.form.get("comment")

        # Update status based on approval/rejection
        if arp == "approve":
            curr_journal.status = "Approved"
            curr_journal.comment = ""
            for transaction in Transaction.query.filter(Transaction.journal_entry_id == curr_journal.id).all():
                account_to_change = Account.query.filter(Account.number == transaction.account_number).first()
                if not account_to_change:
                    continue
                else:
                    print("account found")
                if transaction.to:
                    account_to_change.balance += transaction.amount_changing
                    if transaction.side_for_transaction == 'Debit':
                        account_to_change.debit += transaction.amount_changing
                    else:
                        account_to_change.credit += transaction.amount_changing
                    print("increased")
                else:
                    account_to_change.balance -= transaction.amount_changing
                    if transaction.side_for_transaction == 'Debit':
                        account_to_change.debit -= transaction.amount_changing
                    else:
                        account_to_change.credit -= transaction.amount_changing
                    print("decreased")
                    
                    
        elif arp == "reject":
            curr_journal.comment = comment
            if curr_journal.comment == "":
                flash("Comment Cannot be Empty!", category="error")
                return redirect(url_for("chart.approve_reject", id=ref_id))

            curr_journal.status = "Rejected"
        
        print("committing")
        db.session.commit()
        return redirect(url_for("chart.ledger"))

    return checkRoleClearance(
        current_user.role,
        "manager",
        render_template(
            "approve_reject.html",
            user=current_user,
            dashUser=current_user.role,
            homeRoute="/",
            helpRoute="/help",
            back=url_for("chart.journal_entry", id=ref_id),
            curr_journal=curr_journal,
        ),
    )