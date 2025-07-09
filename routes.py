import os
import csv
import pandas as pd
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import func, extract
from app import app, db
from models import User, Transaction, Goal, Debt, Badge, UserBadge
from insights import generate_insights, predict_spending
from badges import check_and_award_badges, initialize_badges
from categorizer import categorize_transaction
import logging

# Initialize badges on startup
with app.app_context():
    initialize_badges()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('signup.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('signup.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's transactions
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    
    # Calculate basic statistics
    total_income = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    net_worth = total_income - total_expenses
    
    # Get recent transactions
    recent_transactions = transactions[:10]
    
    # Category-wise spending
    category_spending = {}
    for transaction in transactions:
        if transaction.amount < 0:  # Only expenses
            category = transaction.category
            category_spending[category] = category_spending.get(category, 0) + abs(transaction.amount)
    
    # Monthly spending data
    monthly_data = {}
    for transaction in transactions:
        month_key = transaction.date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expenses': 0}
        
        if transaction.amount > 0:
            monthly_data[month_key]['income'] += transaction.amount
        else:
            monthly_data[month_key]['expenses'] += abs(transaction.amount)
    
    # Generate insights
    insights = generate_insights(current_user.id)
    
    # Get user's goals
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    # Get user's badges
    user_badges = UserBadge.query.filter_by(user_id=current_user.id).join(Badge).all()
    
    # Check for new badges
    check_and_award_badges(current_user.id)
    
    return render_template('dashboard.html',
                         total_income=total_income,
                         total_expenses=total_expenses,
                         net_worth=net_worth,
                         recent_transactions=recent_transactions,
                         category_spending=category_spending,
                         monthly_data=monthly_data,
                         insights=insights,
                         goals=goals,
                         user_badges=user_badges)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Process CSV file
                df = pd.read_csv(filepath)
                
                # Validate required columns
                required_columns = ['date', 'amount', 'description']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    flash(f'CSV must contain columns: {", ".join(missing_columns)}', 'error')
                    return redirect(request.url)
                
                # Process transactions
                transactions_added = 0
                errors = []
                
                for index, row in df.iterrows():
                    try:
                        # Parse date
                        date_obj = pd.to_datetime(row['date']).date()
                        
                        # Get amount
                        amount = float(row['amount'])
                        
                        # Get description
                        description = str(row['description']).strip()
                        
                        if not description:
                            errors.append(f"Row {index + 1}: Empty description")
                            continue
                        
                        # Auto-categorize
                        category = categorize_transaction(description)
                        
                        # Create transaction
                        transaction = Transaction(
                            user_id=current_user.id,
                            date=date_obj,
                            amount=amount,
                            description=description,
                            category=category
                        )
                        db.session.add(transaction)
                        transactions_added += 1
                        
                    except Exception as e:
                        errors.append(f"Row {index + 1}: {str(e)}")
                        continue
                
                db.session.commit()
                
                if transactions_added > 0:
                    flash(f'Successfully imported {transactions_added} transactions!', 'success')
                    # Check for new badges
                    check_and_award_badges(current_user.id)
                
                if errors:
                    flash(f'Encountered {len(errors)} errors during import.', 'warning')
                
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                logging.error(f"CSV processing error: {e}")
            
            finally:
                # Clean up uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            flash('Please upload a CSV file.', 'error')
    
    return render_template('upload.html')

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    if request.method == 'POST':
        goal_name = request.form.get('goal_name')
        target_amount = request.form.get('target_amount')
        target_date = request.form.get('target_date')
        
        if not goal_name or not target_amount or not target_date:
            flash('All fields are required.', 'error')
            return redirect(url_for('goals'))
        
        try:
            target_amount = float(target_amount)
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            
            if target_amount <= 0:
                flash('Target amount must be positive.', 'error')
                return redirect(url_for('goals'))
            
            if target_date <= datetime.now().date():
                flash('Target date must be in the future.', 'error')
                return redirect(url_for('goals'))
            
            goal = Goal(
                user_id=current_user.id,
                goal_name=goal_name,
                target_amount=target_amount,
                target_date=target_date
            )
            db.session.add(goal)
            db.session.commit()
            
            flash('Goal created successfully!', 'success')
            
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
        
        return redirect(url_for('goals'))
    
    user_goals = Goal.query.filter_by(user_id=current_user.id).all()
    return render_template('goals.html', goals=user_goals)

@app.route('/update_goal/<int:goal_id>', methods=['POST'])
@login_required
def update_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        flash('Goal not found.', 'error')
        return redirect(url_for('goals'))
    
    try:
        saved_amount = float(request.form.get('saved_amount', 0))
        
        if saved_amount < 0:
            flash('Saved amount cannot be negative.', 'error')
            return redirect(url_for('goals'))
        
        goal.saved_amount = saved_amount
        
        if saved_amount >= goal.target_amount:
            goal.is_completed = True
        
        db.session.commit()
        flash('Goal updated successfully!', 'success')
        
        # Check for new badges
        check_and_award_badges(current_user.id)
        
    except ValueError:
        flash('Invalid amount entered.', 'error')
    
    return redirect(url_for('goals'))

@app.route('/debts', methods=['GET', 'POST'])
@login_required
def debts():
    if request.method == 'POST':
        debt_name = request.form.get('debt_name')
        total_amount = request.form.get('total_amount')
        current_balance = request.form.get('current_balance')
        interest_rate = request.form.get('interest_rate')
        minimum_payment = request.form.get('minimum_payment')
        
        if not all([debt_name, total_amount, current_balance, interest_rate, minimum_payment]):
            flash('All fields are required.', 'error')
            return redirect(url_for('debts'))
        
        try:
            total_amount = float(total_amount)
            current_balance = float(current_balance)
            interest_rate = float(interest_rate)
            minimum_payment = float(minimum_payment)
            
            if total_amount <= 0 or current_balance < 0 or interest_rate < 0 or minimum_payment < 0:
                flash('All amounts must be positive.', 'error')
                return redirect(url_for('debts'))
            
            if current_balance > total_amount:
                flash('Current balance cannot exceed total amount.', 'error')
                return redirect(url_for('debts'))
            
            debt = Debt(
                user_id=current_user.id,
                debt_name=debt_name,
                total_amount=total_amount,
                current_balance=current_balance,
                interest_rate=interest_rate,
                minimum_payment=minimum_payment
            )
            db.session.add(debt)
            db.session.commit()
            
            flash('Debt added successfully!', 'success')
            
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
        
        return redirect(url_for('debts'))
    
    user_debts = Debt.query.filter_by(user_id=current_user.id).all()
    return render_template('debts.html', debts=user_debts)

@app.route('/update_debt/<int:debt_id>', methods=['POST'])
@login_required
def update_debt(debt_id):
    debt = Debt.query.filter_by(id=debt_id, user_id=current_user.id).first()
    if not debt:
        flash('Debt not found.', 'error')
        return redirect(url_for('debts'))
    
    try:
        current_balance = float(request.form.get('current_balance'))
        
        if current_balance < 0:
            flash('Current balance cannot be negative.', 'error')
            return redirect(url_for('debts'))
        
        if current_balance > debt.total_amount:
            flash('Current balance cannot exceed total amount.', 'error')
            return redirect(url_for('debts'))
        
        debt.current_balance = current_balance
        
        db.session.commit()
        flash('Debt updated successfully!', 'success')
        
        # Check for new badges
        check_and_award_badges(current_user.id)
        
    except ValueError:
        flash('Invalid amount entered.', 'error')
    
    return redirect(url_for('debts'))

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    report_type = request.form.get('report_type')
    
    if not start_date_str or not end_date_str or not report_type:
        flash('All fields are required.', 'error')
        return redirect(url_for('reports'))
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if start_date > end_date:
            flash('Start date must be before end date.', 'error')
            return redirect(url_for('reports'))
        
        # Get transactions in date range
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).order_by(Transaction.date.desc()).all()
        
        if not transactions:
            flash('No transactions found in the selected date range.', 'warning')
            return redirect(url_for('reports'))
        
        if report_type == 'csv':
            # Generate CSV report
            filename = f'transactions_{start_date}_{end_date}.csv'
            filepath = os.path.join(app.config['REPORTS_FOLDER'], filename)
            
            with open(filepath, 'w', newline='') as csvfile:
                fieldnames = ['date', 'amount', 'description', 'category']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for transaction in transactions:
                    writer.writerow({
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'amount': transaction.amount,
                        'description': transaction.description,
                        'category': transaction.category
                    })
            
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        elif report_type == 'pdf':
            # Generate PDF report using ReportLab
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            
            filename = f'financial_report_{start_date}_{end_date}.pdf'
            filepath = os.path.join(app.config['REPORTS_FOLDER'], filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph(f'Financial Report - {start_date} to {end_date}', styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Summary
            total_income = sum(t.amount for t in transactions if t.amount > 0)
            total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
            net_worth = total_income - total_expenses
            
            summary_data = [
                ['Metric', 'Amount'],
                ['Total Income', f'${total_income:.2f}'],
                ['Total Expenses', f'${total_expenses:.2f}'],
                ['Net Worth', f'${net_worth:.2f}']
            ]
            
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 12))
            
            # Transactions table
            trans_data = [['Date', 'Amount', 'Description', 'Category']]
            for transaction in transactions[:50]:  # Limit to first 50 transactions
                trans_data.append([
                    transaction.date.strftime('%Y-%m-%d'),
                    f'${transaction.amount:.2f}',
                    transaction.description[:40] + '...' if len(transaction.description) > 40 else transaction.description,
                    transaction.category
                ])
            
            trans_table = Table(trans_data)
            trans_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(trans_table)
            
            if len(transactions) > 50:
                story.append(Spacer(1, 12))
                story.append(Paragraph(f'... and {len(transactions) - 50} more transactions', styles['Normal']))
            
            doc.build(story)
            return send_file(filepath, as_attachment=True, download_name=filename)
        
        else:
            flash('Invalid report type.', 'error')
            return redirect(url_for('reports'))
    
    except ValueError:
        flash('Invalid date format.', 'error')
        return redirect(url_for('reports'))
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        logging.error(f"Report generation error: {e}")
        return redirect(url_for('reports'))

@app.route('/badges')
@login_required
def badges():
    # Get all badges
    all_badges = Badge.query.all()
    
    # Get user's earned badges
    earned_badges = UserBadge.query.filter_by(user_id=current_user.id).all()
    earned_badge_ids = [ub.badge_id for ub in earned_badges]
    
    return render_template('badges.html', all_badges=all_badges, earned_badge_ids=earned_badge_ids)

@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction deleted successfully!', 'success')
    else:
        flash('Transaction not found.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_goal/<int:goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if goal:
        db.session.delete(goal)
        db.session.commit()
        flash('Goal deleted successfully!', 'success')
    else:
        flash('Goal not found.', 'error')
    
    return redirect(url_for('goals'))

@app.route('/delete_debt/<int:debt_id>', methods=['POST'])
@login_required
def delete_debt(debt_id):
    debt = Debt.query.filter_by(id=debt_id, user_id=current_user.id).first()
    if debt:
        db.session.delete(debt)
        db.session.commit()
        flash('Debt deleted successfully!', 'success')
    else:
        flash('Debt not found.', 'error')
    
    return redirect(url_for('debts'))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(413)
def too_large(error):
    flash('File too large. Please upload a file smaller than 16MB.', 'error')
    return redirect(url_for('upload'))
