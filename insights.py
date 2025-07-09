import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func
from models import Transaction, Goal, Debt
from app import db
import logging

def generate_insights(user_id):
    """Generate financial insights for a user"""
    insights = []
    
    # Get user's transactions
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    
    if not transactions:
        return ["Upload some transactions to get personalized insights!"]
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame([{
        'date': t.date,
        'amount': t.amount,
        'category': t.category,
        'description': t.description
    } for t in transactions])
    
    # Monthly spending analysis
    current_month = datetime.now().month
    current_year = datetime.now().year
    last_month = current_month - 1 if current_month > 1 else 12
    last_month_year = current_year if current_month > 1 else current_year - 1
    
    current_month_expenses = df[
        (df['date'].dt.month == current_month) & 
        (df['date'].dt.year == current_year) & 
        (df['amount'] < 0)
    ]['amount'].sum()
    
    last_month_expenses = df[
        (df['date'].dt.month == last_month) & 
        (df['date'].dt.year == last_month_year) & 
        (df['amount'] < 0)
    ]['amount'].sum()
    
    if abs(last_month_expenses) > 0:
        spending_change = ((abs(current_month_expenses) - abs(last_month_expenses)) / abs(last_month_expenses)) * 100
        if spending_change > 10:
            insights.append(f"⚠️ Your spending increased by {spending_change:.1f}% this month!")
        elif spending_change < -10:
            insights.append(f"✅ Great job! You reduced spending by {abs(spending_change):.1f}% this month!")
    
    # Category-wise insights
    expense_df = df[df['amount'] < 0].copy()
    if not expense_df.empty:
        category_spending = expense_df.groupby('category')['amount'].sum().abs()
        if len(category_spending) > 0:
            top_category = category_spending.idxmax()
            top_amount = category_spending.max()
            
            insights.append(f"💰 Your highest spending category is '{top_category}' with ${top_amount:.2f}")
            
            # Check for unusual spending patterns
            category_avg = expense_df.groupby('category')['amount'].mean().abs()
            recent_transactions = expense_df[expense_df['date'] >= datetime.now().date() - timedelta(days=7)]
            
            if not recent_transactions.empty:
                recent_category_spending = recent_transactions.groupby('category')['amount'].sum().abs()
                for category in recent_category_spending.index:
                    if category in category_avg.index:
                        recent_amount = recent_category_spending[category]
                        avg_amount = category_avg[category] * 7  # Weekly average
                        if recent_amount > avg_amount * 1.5:
                            insights.append(f"📈 You spent 50% more than usual on '{category}' this week!")
    
    # Income insights
    income_df = df[df['amount'] > 0]
    if not income_df.empty:
        total_income = income_df['amount'].sum()
        total_expenses = abs(expense_df['amount'].sum()) if not expense_df.empty else 0
        
        if total_income > 0:
            savings_rate = ((total_income - total_expenses) / total_income) * 100
            if savings_rate > 20:
                insights.append(f"🎉 Excellent! You're saving {savings_rate:.1f}% of your income!")
            elif savings_rate < 10:
                insights.append(f"💡 Consider increasing your savings rate. Currently at {savings_rate:.1f}%")
            elif savings_rate < 0:
                insights.append(f"⚠️ You're spending more than you earn. Consider reducing expenses.")
    
    # Goal progress insights
    goals = Goal.query.filter_by(user_id=user_id).all()
    for goal in goals:
        if goal.progress_percentage > 75:
            insights.append(f"🎯 You're {goal.progress_percentage:.1f}% towards your '{goal.goal_name}' goal!")
        elif goal.target_date < datetime.now().date() and not goal.is_completed:
            insights.append(f"⏰ Your '{goal.goal_name}' goal deadline has passed. Time to reassess!")
    
    # Debt insights
    debts = Debt.query.filter_by(user_id=user_id).all()
    if debts:
        total_debt = sum(debt.current_balance for debt in debts)
        if total_debt > 0:
            highest_interest_debt = max(debts, key=lambda d: d.interest_rate)
            insights.append(f"💳 Focus on paying off '{highest_interest_debt.debt_name}' first - it has the highest interest rate ({highest_interest_debt.interest_rate:.1f}%)")
    
    # Transaction frequency insights
    if len(transactions) > 30:
        avg_transactions_per_day = len(transactions) / (df['date'].max() - df['date'].min()).days
        if avg_transactions_per_day > 3:
            insights.append(f"📊 You make an average of {avg_transactions_per_day:.1f} transactions per day")
    
    # Seasonal spending patterns
    if len(df) > 100:
        monthly_spending = df[df['amount'] < 0].groupby(df['date'].dt.month)['amount'].sum().abs()
        if len(monthly_spending) > 0:
            highest_month = monthly_spending.idxmax()
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            insights.append(f"📅 You tend to spend most in {month_names[highest_month-1]}")
    
    return insights[:8] if insights else ["Keep tracking your expenses to get personalized insights!"]

def predict_spending(user_id, category=None):
    """Predict next month's spending using simple linear regression"""
    try:
        from sklearn.linear_model import LinearRegression
        import numpy as np
        
        # Get historical data
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        
        if len(transactions) < 6:
            return None
        
        # Create monthly spending data
        df = pd.DataFrame([{
            'date': t.date,
            'amount': abs(t.amount) if t.amount < 0 else 0,
            'category': t.category
        } for t in transactions])
        
        # Filter by category if specified
        if category:
            df = df[df['category'] == category]
        
        # Group by month
        df['month'] = df['date'].dt.to_period('M')
        monthly_spending = df.groupby('month')['amount'].sum()
        
        if len(monthly_spending) < 3:
            return None
        
        # Prepare data for regression
        X = np.array(range(len(monthly_spending))).reshape(-1, 1)
        y = monthly_spending.values
        
        # Fit model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next month
        next_month_prediction = model.predict([[len(monthly_spending)]])[0]
        
        return max(0, next_month_prediction)
        
    except Exception as e:
        logging.error(f"Error in spending prediction: {e}")
        return None

def get_spending_trends(user_id):
    """Get spending trends over time"""
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    
    if not transactions:
        return {}
    
    df = pd.DataFrame([{
        'date': t.date,
        'amount': t.amount,
        'category': t.category
    } for t in transactions])
    
    # Monthly trends
    df['month'] = df['date'].dt.to_period('M')
    monthly_data = df.groupby('month').agg({
        'amount': lambda x: {
            'income': x[x > 0].sum(),
            'expenses': abs(x[x < 0].sum())
        }
    })
    
    return monthly_data.to_dict()

def get_category_insights(user_id):
    """Get detailed category-wise insights"""
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    
    if not transactions:
        return {}
    
    expense_transactions = [t for t in transactions if t.amount < 0]
    category_data = {}
    
    for transaction in expense_transactions:
        category = transaction.category
        if category not in category_data:
            category_data[category] = {
                'total': 0,
                'count': 0,
                'average': 0
            }
        
        category_data[category]['total'] += abs(transaction.amount)
        category_data[category]['count'] += 1
    
    # Calculate averages
    for category in category_data:
        category_data[category]['average'] = category_data[category]['total'] / category_data[category]['count']
    
    return category_data

def get_financial_health_score(user_id):
    """Calculate a financial health score out of 100"""
    try:
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        
        if not transactions:
            return 0
        
        score = 0
        max_score = 100
        
        # Calculate income vs expenses ratio (30 points)
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
        
        if total_income > 0:
            savings_rate = (total_income - total_expenses) / total_income
            if savings_rate > 0.2:
                score += 30
            elif savings_rate > 0.1:
                score += 20
            elif savings_rate > 0:
                score += 10
        
        # Goal completion rate (25 points)
        goals = Goal.query.filter_by(user_id=user_id).all()
        if goals:
            completed_goals = sum(1 for g in goals if g.is_completed)
            completion_rate = completed_goals / len(goals)
            score += int(completion_rate * 25)
        
        # Debt management (25 points)
        debts = Debt.query.filter_by(user_id=user_id).all()
        if debts:
            total_debt = sum(d.current_balance for d in debts)
            if total_debt == 0:
                score += 25
            elif total_debt < total_income * 0.3:
                score += 20
            elif total_debt < total_income * 0.5:
                score += 15
            elif total_debt < total_income:
                score += 10
        else:
            score += 25  # No debt is good
        
        # Consistency (20 points)
        if len(transactions) > 30:
            recent_transactions = [t for t in transactions if t.date >= datetime.now().date() - timedelta(days=30)]
            if len(recent_transactions) >= 10:
                score += 20
            elif len(recent_transactions) >= 5:
                score += 15
            elif len(recent_transactions) >= 1:
                score += 10
        
        return min(score, max_score)
        
    except Exception as e:
        logging.error(f"Error calculating financial health score: {e}")
        return 0
