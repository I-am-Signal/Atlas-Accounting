from . import db
from flask_login import UserMixin
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func
from datetime import datetime, timedelta

class BaseColumnMixin():
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime, default=datetime.now())
    modify_date = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

class CreatedByMixin():
    __abstract__ = True
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))



class User(db.Model, UserMixin, BaseColumnMixin):
    __tablename__ = 'user'
    is_activated = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    addr_line_1 = db.Column(db.String(200))
    addr_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(200))
    county = db.Column(db.String(200))
    state = db.Column(db.String(2))
    dob = db.Column(db.Date)
    # 'user' 'manager' 'administrator'
    role = db.Column(db.String(13), default='user')
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    
    # couldn't get the CheckConstraint to work in time, plz fix
    # __table_args__ = (
    #     CheckConstraint("role IN (\'administrator\', \'manager\', \'user\')", name="role_check")
    # )
    
    passwords = db.relationship('Credential')
    
class Image(db.Model, BaseColumnMixin):
    __tablename__ = 'image'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_name = db.Column(db.String(150))
    file_mime = db.Column(db.String(1000))
    file_data = db.Column(db.BLOB)
    
    db.relationship('User', backref='profile_picture', foreign_keys=['user_id'])

class Credential(db.Model, BaseColumnMixin):
    __tablename__ = 'credential'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    password = db.Column(db.String(150))
    failedAttempts = db.Column(db.Integer, default=0)
    expirationDate = db.Column(db.DateTime, default=lambda: datetime.now() + timedelta(days=365))

class Company(db.Model, BaseColumnMixin):
    __tablename__ = 'company'
    creator_of_company = db.Column(db.Integer, db.ForeignKey('user.id'))

    db.relationship('User', backref='companies_created', foreign_keys=[creator_of_company])
    
# This may be a better way to do Company vvv
# class Company(db.Model, BaseColumnMixin, CreatedByMixin):
#     db.relationship('User', backref='companies_created', foreign_keys=[CreatedByMixin.created_by])
    
    
class Suspension(db.Model, BaseColumnMixin, CreatedByMixin):
    __tablename__ = 'suspension'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    suspension_start_date = db.Column(db.DateTime)
    suspension_end_date = db.Column(db.DateTime)
    
    db.relationship('User', backref='suspension', foreign_keys=[user_id])

class Account(db.Model, BaseColumnMixin, CreatedByMixin):
    __tablename__ = 'account'
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    number = db.Column(db.Integer)
    name = db.Column(db.String(150))
    description = db.Column(db.String(500))
    normal_side = db.Column(db.String(150))
    category = db.Column(db.String(150))
    subcategory = db.Column(db.String(150))
    initial_balance = db.Column(db.Float, default = 0.0)
    debit = db.Column(db.Float, default = 0.0)
    credit = db.Column(db.Float, default = 0.0)
    balance = db.Column(db.Float, default = 0.0)
    order = db.Column(db.Integer, default = 0)
    statement = db.Column(db.String(150))
    comment = db.Column(db.String(150))
    is_activated = db.Column(db.Boolean, default=True, nullable=False)
    
    db.relationship('User', backref='account_created_by', foreign_keys=[CreatedByMixin.created_by])
    

class Event(db.Model, BaseColumnMixin,CreatedByMixin):
    __tablename__ = 'event'
    
    is_new = db.Column(db.Boolean)
    number = db.Column(db.Integer)
    name = db.Column(db.String(150))
    description = db.Column(db.String(500))
    normal_side = db.Column(db.String(150))
    category = db.Column(db.String(150))
    subcategory = db.Column(db.String(150))
    initial_balance = db.Column(db.Float, default = 0.0)
    debit = db.Column(db.Float, default = 0.0)
    credit = db.Column(db.Float, default = 0.0)
    balance = db.Column(db.Float, default = 0.0)
    order = db.Column(db.Integer, default = 0)
    statement = db.Column(db.String(150))
    comment = db.Column(db.String(150))
    
class Journal_Entry(db.Model, BaseColumnMixin, CreatedByMixin):
    __tablename__ = 'journal_entry'
    # 'Approved' 'Pending' 'Rejected'
    status = db.Column(db.String(150), default='Pending', nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    entry_type =  db.Column(db.String(150), default='Transfer', nullable=False)
    description = db.Column(db.String(150), nullable=False)
    
class Transaction(db.Model, BaseColumnMixin, CreatedByMixin):
    __tablename__ = 'transaction'
    journal_entry_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=False)
    side_for_transaction = db.Column(db.String(150), nullable=False)
    account_number = db.Column(db.Integer, db.ForeignKey('account.number'), nullable=False)
    amount_changing = db.Column(db.Float, nullable=False)
    to = db.Column(db.Boolean, nullable=False, default=False)
