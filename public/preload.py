from flask_login import current_user
from .models import Account, Event
from json import load

def load_accounts():
    """
    Used to load the basic accounts of a business\n
    To use this method, simply plug it into one of the endpoint calls and 
    then remove it once it has
    """
        
    from . import db
    with open("public/preload.json", 'r') as json_file:
        accounts = load(json_file)
    
    for account in accounts:
        if not db.session.query(Account).filter(Account.number == account["number"]).first():
            new_account = Account(
                number=account["number"],
                name=account["name"],
                description=None,
                normal_side=account["normal_side"],  # check for valid normal side
                category=account["category"],
                subcategory=account["subcategory"],
                initial_balance=account["initial_balance"],  # check if valid
                balance=account["initial_balance"],
                order=account["order"],  # check if > 0, is int, and is not the same for the cat/subcat
                statement=account["statement"],  # check if valid statement type
                comment=None,
                created_by=current_user.id,
                company_id=current_user.company_id,
            )
            db.session.add(new_account)

            db.session.add(Event(
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
            ))
    
    db.session.commit()