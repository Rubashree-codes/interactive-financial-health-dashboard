# Financial Dashboard - Replit Configuration

## Overview

This is a comprehensive personal finance management web application built with Flask. It provides expense tracking, goal setting, debt management, and intelligent financial insights with a gamification system for user engagement.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 with Bootstrap 5 for responsive UI
- **JavaScript Libraries**: Chart.js for data visualization, vanilla JS for interactivity
- **CSS Framework**: Bootstrap 5 with custom CSS variables for consistent theming
- **Icons**: Font Awesome for comprehensive icon library

### Backend Architecture
- **Web Framework**: Flask with modular route structure
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy integration
- **Authentication**: Flask-Login for session management
- **File Processing**: Pandas for CSV data processing and analysis

### Database Schema
- **Users**: Authentication and user profile management
- **Transactions**: Financial transaction records with categorization
- **Goals**: Financial goal tracking with progress monitoring
- **Debts**: Debt management with payment tracking
- **Badges**: Achievement system for user engagement
- **UserBadges**: Junction table for user-badge relationships

## Key Components

### Authentication System
- Password hashing with Werkzeug security
- Session management with Flask-Login
- User registration and login forms with validation
- Protected routes with login_required decorator

### Transaction Management
- CSV upload and processing functionality
- Automatic transaction categorization using keyword matching
- Real-time financial analytics and insights
- Data export capabilities (CSV/PDF)

### Goal and Debt Tracking
- CRUD operations for financial goals
- Progress tracking with visual indicators
- Debt management with payment scheduling
- Achievement system with badge rewards

### Reporting System
- PDF report generation using ReportLab
- CSV export functionality
- Financial insights and spending analysis
- Predictive analytics for spending patterns

### Gamification System
- Achievement badges for financial milestones
- Progress tracking and motivational feedback
- User engagement through visual progress indicators

## Data Flow

1. **User Registration/Login**: Authentication → Session Creation → Dashboard Access
2. **Transaction Upload**: CSV File → Pandas Processing → Categorization → Database Storage
3. **Goal Management**: User Input → Validation → Progress Calculation → Database Update
4. **Debt Tracking**: Debt Creation → Payment Recording → Progress Monitoring → Badge Awards
5. **Report Generation**: Date Range Selection → Data Query → PDF/CSV Generation → File Download

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **Pandas**: Data processing and analysis
- **Chart.js**: Client-side data visualization
- **Bootstrap 5**: CSS framework and components
- **Font Awesome**: Icon library

### Optional Dependencies
- **ReportLab**: PDF generation for reports
- **Werkzeug**: Security utilities for password hashing
- **Logging**: Python standard library for debugging

## Deployment Strategy

### Development Environment
- SQLite database for local development
- Debug mode enabled with detailed error pages
- File uploads stored in local directories
- Hot reload for development efficiency

### Production Considerations
- Environment variables for sensitive configuration
- Database connection pooling with SQLAlchemy
- File upload size limits (16MB maximum)
- ProxyFix middleware for reverse proxy compatibility
- Secure session key management

### File Structure
- **Static assets**: CSS, JS, and images in `/static`
- **Templates**: Jinja2 templates in `/templates`
- **Upload directory**: `/uploads` for temporary CSV files
- **Reports directory**: `/reports` for generated PDF reports

### Security Features
- Password hashing with salt
- CSRF protection through Flask-WTF integration
- File upload validation and sanitization
- User data isolation through foreign key constraints
- Session-based authentication with secure cookies

The application uses a modular architecture with separate concerns for authentication, data processing, visualization, and reporting, making it maintainable and scalable.