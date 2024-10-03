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

class User(db.Model, UserMixin, BaseColumnMixin):
    is_activated = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    
    # may be better to store elsewhere, keeping the pathway to reach it
    # would need to implement a method to retrieve and display if stored locally
    # picture = db.Column(db.BLOB)
    
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    addr_line_1 = db.Column(db.String(200))
    addr_line_2 = db.Column(db.String(200))
    city = db.Column(db.String(200))
    county = db.Column(db.String(200))
    state = db.Column(db.String(2))
    dob = db.Column(db.Date)
    role = db.Column(db.String(13), default='user')
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    
    # couldn't get the CheckConstraint to work in time, plz fix
    # __table_args__ = (
    #     CheckConstraint("role IN (\'administrator\', \'manager\', \'user\')", name="role_check")
    # )
    
    passwords = db.relationship('Credential')

class Credential(db.Model, BaseColumnMixin):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    password = db.Column(db.String(150))
    failedAttempts = db.Column(db.Integer, default=0)
    expirationDate = db.Column(db.DateTime, default=lambda: datetime.now() + timedelta(days=365))

class Company(db.Model, BaseColumnMixin):
    creator_of_company = db.Column(db.Integer, db.ForeignKey('user.id'))

    db.relationship('User', backref='companies_created', foreign_keys=[creator_of_company])
    
class Suspension(db.Model, BaseColumnMixin):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    suspension_start_date = db.Column(db.DateTime)
    suspension_end_date = db.Column(db.DateTime)
    
    db.relationship('User', backref='suspension', foreign_keys=[user_id])