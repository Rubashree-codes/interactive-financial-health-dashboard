from datetime import datetime, timedelta
from sqlalchemy import func
from models import User, Transaction, Goal, Debt, Badge, UserBadge
from app import db
import logging

def initialize_badges():
    """Initialize the badge system with predefined badges"""
    badges_data = [
        {
            'name': 'First Transaction',
            'description': 'Upload your first transaction',
            'icon': '🎯',
            'condition': 'first_transaction'
        },
        {
            'name': 'Saver',
            'description': 'Save money for 3 consecutive months',
            'icon': '💰',
            'condition': 'consecutive_savings'
        },
        {
            'name': 'Goal Achiever',
            'description': 'Complete your first financial goal',
            'icon': '🏆',
            'condition': 'first_goal_completed'
        },
        {
            'name': 'Debt Slayer',
            'description': 'Pay off any debt completely',
            'icon': '⚔️',
            'condition': 'debt_paid_off'
        },
        {
            'name': 'Budget Master',
            'description': 'Keep expenses under control for a month',
            'icon': '📊',
            'condition': 'budget_control'
        },
        {
            'name': 'Consistent Tracker',
            'description': 'Track expenses for 30 consecutive days',
            'icon': '📈',
            'condition': 'consistent_tracking'
        },
        {
            'name': 'Big Spender',
            'description': 'Record a transaction over $1000',
            'icon': '💸',
            'condition': 'big_transaction'
        },
        {
            'name': 'Categorization Pro',
            'description': 'Have transactions in 10 different categories',
            'icon': '🏷️',
            'condition': 'category_diversity'
        },
        {
            'name': 'Emergency Fund',
            'description': 'Save 3 months of expenses',
            'icon': '🛡️',
            'condition': 'emergency_fund'
        },
        {
            'name': 'Century Club',
            'description': 'Record 100 transactions',
            'icon': '💯',
            'condition': 'hundred_transactions'
        },
        {
            'name': 'Income Earner',
            'description': 'Record your first income transaction',
            'icon': '💵',
            'condition': 'first_income'
        },
        {
            'name': 'Monthly Tracker',
            'description': 'Track transactions for a full month',
            'icon': '📅',
            'condition': 'monthly_tracking'
        },
        {
            'name': 'Expense Cutter',
            'description': 'Reduce monthly expenses by 20%',
            'icon': '✂️',
            'condition': 'expense_reduction'
        },
        {
            'name': 'Goal Setter',
            'description': 'Create your first financial goal',
            'icon': '🎯',
            'condition': 'first_goal_set'
        },
        {
            'name': 'Debt Tracker',
            'description': 'Add your first debt to track',
            'icon': '📋',
            'condition': 'first_debt_added'
        }
    ]
    
    for badge_data in badges_data:
        existing_badge = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing_badge:
            badge = Badge(
                name=badge_data['name'],
                description=badge_data['description'],
                icon=badge_data['icon'],
                condition=badge_data['condition']
            )
            db.session.add(badge)
    
    try:
        db.session.commit()
        logging.info("Badges initialized successfully")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error initializing badges: {e}")

def check_and_award_badges(user_id):
    """Check if user has earned any new badges and award them"""
    user = User.query.get(user_id)
    if not user:
        return []
    
    # Get all badges and user's earned badges
    all_badges = Badge.query.all()
    earned_badges = UserBadge.query.filter_by(user_id=user_id).all()
    earned_badge_ids = [ub.badge_id for ub in earned_badges]
    
    newly_earned = []
    
    for badge in all_badges:
        if badge.id in earned_badge_ids:
            continue  # Already earned
        
        if check_badge_condition(user_id, badge.condition):
            # Award badge
            user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
            db.session.add(user_badge)
            newly_earned.append(badge.name)
    
    if newly_earned:
        try:
            db.session.commit()
            logging.info(f"User {user_id} earned badges: {newly_earned}")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error awarding badges: {e}")
    
    return newly_earned

def check_badge_condition(user_id, condition):
    """Check if a specific badge condition is met"""
    try:
        if condition == 'first_transaction':
            return Transaction.query.filter_by(user_id=user_id).count() >= 1
        
        elif condition == 'first_income':
            return Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.amount > 0
            ).count() >= 1
        
        elif condition == 'consecutive_savings':
            # Check if user has positive savings for 3 consecutive months
            transactions = Transaction.query.filter_by(user_id=user_id).all()
            if not transactions:
                return False
            
            # Group by month and calculate net savings
            monthly_savings = {}
            for transaction in transactions:
                month_key = transaction.date.strftime('%Y-%m')
                monthly_savings[month_key] = monthly_savings.get(month_key, 0) + transaction.amount
            
            # Check for 3 consecutive months of positive savings
            sorted_months = sorted(monthly_savings.keys())
            if len(sorted_months) < 3:
                return False
            
            consecutive_count = 0
            for month in sorted_months:
                if monthly_savings[month] > 0:
                    consecutive_count += 1
                    if consecutive_count >= 3:
                        return True
                else:
                    consecutive_count = 0
            
            return False
        
        elif condition == 'first_goal_completed':
            return Goal.query.filter_by(user_id=user_id, is_completed=True).count() >= 1
        
        elif condition == 'first_goal_set':
            return Goal.query.filter_by(user_id=user_id).count() >= 1
        
        elif condition == 'first_debt_added':
            return Debt.query.filter_by(user_id=user_id).count() >= 1
        
        elif condition == 'debt_paid_off':
            debts = Debt.query.filter_by(user_id=user_id).all()
            return any(debt.current_balance == 0 for debt in debts)
        
        elif condition == 'budget_control':
            # Check if expenses were under a reasonable limit last month
            last_month_start = datetime.now().replace(day=1) - timedelta(days=1)
            last_month_start = last_month_start.replace(day=1)
            last_month_end = datetime.now().replace(day=1) - timedelta(days=1)
            
            monthly_expenses = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.date >= last_month_start.date(),
                Transaction.date <= last_month_end.date(),
                Transaction.amount < 0
            ).all()
            
            if not monthly_expenses:
                return False
            
            total_expenses = sum(abs(t.amount) for t in monthly_expenses)
            monthly_income = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.date >= last_month_start.date(),
                Transaction.date <= last_month_end.date(),
                Transaction.amount > 0
            ).all()
            
            total_income = sum(t.amount for t in monthly_income)
            
            # Budget control: expenses less than 80% of income
            return total_income > 0 and total_expenses < (total_income * 0.8)
        
        elif condition == 'consistent_tracking':
            # Check if user has transactions in last 30 days
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            recent_transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.date >= thirty_days_ago
            ).all()
            
            # Check if there are transactions in at least 20 of the last 30 days
            transaction_dates = set(t.date for t in recent_transactions)
            return len(transaction_dates) >= 20
        
        elif condition == 'monthly_tracking':
            # Check if user has transactions spanning at least 30 days
            transactions = Transaction.query.filter_by(user_id=user_id).all()
            if len(transactions) < 10:
                return False
            
            dates = [t.date for t in transactions]
            date_range = max(dates) - min(dates)
            return date_range.days >= 30
        
        elif condition == 'big_transaction':
            return Transaction.query.filter(
                Transaction.user_id == user_id,
                func.abs(Transaction.amount) >= 1000
            ).count() >= 1
        
        elif condition == 'category_diversity':
            categories = db.session.query(Transaction.category).filter_by(user_id=user_id).distinct().all()
            return len(categories) >= 10
        
        elif condition == 'emergency_fund':
            # Check if user has savings worth 3 months of expenses
            transactions = Transaction.query.filter_by(user_id=user_id).all()
            if not transactions:
                return False
            
            # Calculate average monthly expenses
            monthly_expenses = {}
            for transaction in transactions:
                if transaction.amount < 0:
                    month_key = transaction.date.strftime('%Y-%m')
                    monthly_expenses[month_key] = monthly_expenses.get(month_key, 0) + abs(transaction.amount)
            
            if not monthly_expenses:
                return False
            
            avg_monthly_expenses = sum(monthly_expenses.values()) / len(monthly_expenses)
            
            # Calculate total savings
            total_savings = sum(t.amount for t in transactions if t.amount > 0)
            total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
            net_savings = total_savings - total_expenses
            
            return net_savings >= (avg_monthly_expenses * 3)
        
        elif condition == 'hundred_transactions':
            return Transaction.query.filter_by(user_id=user_id).count() >= 100
        
        elif condition == 'expense_reduction':
            # Check if user reduced expenses by 20% from previous month
            current_month = datetime.now().month
            current_year = datetime.now().year
            last_month = current_month - 1 if current_month > 1 else 12
            last_month_year = current_year if current_month > 1 else current_year - 1
            
            current_expenses = Transaction.query.filter(
                Transaction.user_id == user_id,
                func.extract('month', Transaction.date) == current_month,
                func.extract('year', Transaction.date) == current_year,
                Transaction.amount < 0
            ).all()
            
            last_month_expenses = Transaction.query.filter(
                Transaction.user_id == user_id,
                func.extract('month', Transaction.date) == last_month,
                func.extract('year', Transaction.date) == last_month_year,
                Transaction.amount < 0
            ).all()
            
            if not current_expenses or not last_month_expenses:
                return False
            
            current_total = sum(abs(t.amount) for t in current_expenses)
            last_month_total = sum(abs(t.amount) for t in last_month_expenses)
            
            if last_month_total == 0:
                return False
            
            reduction = (last_month_total - current_total) / last_month_total
            return reduction >= 0.2
        
        else:
            logging.warning(f"Unknown badge condition: {condition}")
            return False
    
    except Exception as e:
        logging.error(f"Error checking badge condition {condition}: {e}")
        return False

def get_badge_progress(user_id):
    """Get progress towards unearned badges"""
    progress = {}
    
    # Get earned badges
    earned_badges = UserBadge.query.filter_by(user_id=user_id).all()
    earned_badge_ids = [ub.badge_id for ub in earned_badges]
    
    # Get all badges
    all_badges = Badge.query.all()
    
    for badge in all_badges:
        if badge.id in earned_badge_ids:
            continue
        
        progress[badge.name] = calculate_badge_progress(user_id, badge.condition)
    
    return progress

def calculate_badge_progress(user_id, condition):
    """Calculate progress percentage for a badge condition"""
    try:
        if condition == 'first_transaction':
            count = Transaction.query.filter_by(user_id=user_id).count()
            return min(100, count * 100)
        
        elif condition == 'hundred_transactions':
            count = Transaction.query.filter_by(user_id=user_id).count()
            return min(100, count)
        
        elif condition == 'category_diversity':
            categories = db.session.query(Transaction.category).filter_by(user_id=user_id).distinct().all()
            return min(100, len(categories) * 10)
        
        elif condition == 'first_goal_completed':
            completed_goals = Goal.query.filter_by(user_id=user_id, is_completed=True).count()
            return min(100, completed_goals * 100)
        
        elif condition == 'first_goal_set':
            goals = Goal.query.filter_by(user_id=user_id).count()
            return min(100, goals * 100)
        
        elif condition == 'consistent_tracking':
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            recent_transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                Transaction.date >= thirty_days_ago
            ).all()
            
            transaction_dates = set(t.date for t in recent_transactions)
            return min(100, (len(transaction_dates) / 20) * 100)
        
        else:
            return 0
    
    except Exception as e:
        logging.error(f"Error calculating badge progress for {condition}: {e}")
        return 0
