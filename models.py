from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    debts = db.relationship('Debt', backref='user', lazy=True, cascade='all, delete-orphan')
    badges = db.relationship('UserBadge', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.description}: {self.amount}>'

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    saved_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_completed = db.Column(db.Boolean, default=False)
    
    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return min(100, (self.saved_amount / self.target_amount) * 100)
    
    def __repr__(self):
        return f'<Goal {self.goal_name}: {self.saved_amount}/{self.target_amount}>'

class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    debt_name = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    current_balance = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    minimum_payment = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def paid_amount(self):
        return self.total_amount - self.current_balance
    
    @property
    def progress_percentage(self):
        if self.total_amount == 0:
            return 0
        return min(100, (self.paid_amount / self.total_amount) * 100)
    
    def __repr__(self):
        return f'<Debt {self.debt_name}: {self.current_balance}/{self.total_amount}>'

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Badge {self.name}>'

class UserBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    badge = db.relationship('Badge', backref='user_badges')
    
    def __repr__(self):
        return f'<UserBadge {self.user_id}: {self.badge_id}>'
