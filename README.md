# Personal Finance Dashboard

A comprehensive web-based personal finance management system built with Flask, featuring expense tracking, goal setting, debt management, and intelligent financial insights.

## Features

### 🏦 Core Financial Management
- **CSV Transaction Upload**: Import bank statements and transactions
- **Automatic Categorization**: Smart categorization using pattern recognition
- **Interactive Charts**: Beautiful visualizations with Chart.js
- **Real-time Analytics**: Live financial insights and trends

### 🎯 Goal & Debt Management
- **Financial Goals**: Set and track savings goals with progress indicators
- **Debt Tracking**: Monitor debt payoff with strategic recommendations
- **Progress Visualization**: Visual progress bars and completion tracking

### 📊 Reports & Analytics
- **PDF Reports**: Professional financial summary reports
- **CSV Export**: Download transaction data for external analysis
- **Smart Insights**: AI-powered spending analysis and recommendations
- **Spending Trends**: Detailed category-wise spending patterns

### 🏆 Gamification
- **Achievement Badges**: Earn badges for financial milestones
- **Progress Tracking**: Visual progress indicators
- **Motivational System**: Encouraging feedback and tips

### 🔒 Security & Privacy
- **User Authentication**: Secure login system with password hashing
- **Data Protection**: Local SQLite database with user isolation
- **Secure File Handling**: Safe CSV upload with validation

## Screenshots

### Dashboard Overview
![Dashboard](static/images/dashboard-preview.png)

### Goal Tracking
![Goals](static/images/goals-preview.png)

### Debt Management
![Debts](static/images/debts-preview.png)

## Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **Flask-Login** - User session management
- **Pandas** - Data processing and analysis
- **ReportLab** - PDF report generation
- **scikit-learn** - Machine learning for insights

### Frontend
- **Bootstrap 5** - Responsive UI framework
- **Chart.js** - Interactive charts and graphs
- **Font Awesome** - Icons
- **Custom CSS** - Modern gradient design
- **Vanilla JavaScript** - Interactive features

### Database
- **SQLite** - Local database storage
- **SQLAlchemy ORM** - Database models and relationships

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/financial-dashboard.git
   cd financial-dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-login pandas scikit-learn reportlab werkzeug
   ```

4. **Set environment variables**
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   export DATABASE_URL="sqlite:///financial_dashboard.db"
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the dashboard**
   Open your browser and go to `http://localhost:5000`

## Usage Guide

### 1. Account Setup
- Create an account using the signup form
- Log in with your credentials
- Start with the dashboard overview

### 2. Import Transactions
- Go to the Upload page
- Download the sample CSV template
- Upload your bank transaction CSV file
- Review auto-categorized transactions

### 3. Set Financial Goals
- Navigate to the Goals page
- Create savings goals with target amounts and dates
- Update progress as you save
- Track completion percentage

### 4. Manage Debts
- Add debts with interest rates and payment information
- Update balances as you make payments
- View payoff strategies and recommendations
- Track progress toward debt freedom

### 5. Generate Reports
- Go to the Reports page
- Select date ranges
- Export CSV data or generate PDF summaries
- Use reports for tax preparation or analysis

### 6. Earn Badges
- Complete financial activities to earn achievement badges
- Track your progress toward financial milestones
- Stay motivated with gamification elements

## CSV Format

Your transaction CSV should contain these columns:

```csv
date,amount,description
2024-01-15,2500.00,Salary deposit
2024-01-16,-45.50,Grocery shopping
2024-01-17,-12.00,Coffee purchase
