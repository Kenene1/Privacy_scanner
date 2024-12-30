from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from app import db
from app.models import User, ScanResult
from flask_bcrypt import Bcrypt
import logging

# Initialize Flask-Bcrypt for password hashing
bcrypt = Bcrypt()

# Create the Blueprint for the routes
routes_bp = Blueprint('routes', __name__)

# Setup logging for errors
logger = logging.getLogger(__name__)

# Login Form using Flask-WTF
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Registration Form using Flask-WTF
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# Home page route
@routes_bp.route('/')
def home():
    """Home page for the application."""
    return render_template('index.html')

# About page route
@routes_bp.route('/about')
def about():
    """About page for the application."""
    return render_template('about.html')

# Login route for user authentication
@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query the database to find the user by username
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login Successful!', 'success')
            return redirect(url_for('routes.home'))

        flash('Login Unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html', form=form)

# Logout route for ending the user's session
@routes_bp.route('/logout')
@login_required
def logout():
    """Log the user out."""
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('routes.home'))

# Registration route to allow new users to sign up
@routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', form=form)

# Route to start the privacy scan (protected)
@routes_bp.route('/scan/start', methods=['POST'])
@login_required
def start_scan():
    """Initiates a privacy scan."""
    try:
        # Sample scan logic (replace with real scan logic)
        scan_data = {"scan_status": "completed", "details": "No privacy issues found."}
        
        # Log the start of the scan
        logger.info(f"User {current_user.username} started a scan.")

        # Store the scan result in the database
        scan_result = ScanResult(user_id=current_user.id, scan_data=scan_data)
        db.session.add(scan_result)
        db.session.commit()
        
        return jsonify(scan_data), 200
    except Exception as e:
        # Log any error during the scan process
        logger.error(f"Error during scan for user {current_user.username}: {e}")
        return jsonify({"error": "Scan failed. Please try again."}), 500

# Route to view the scan results (protected)
@routes_bp.route('/scan/results/<int:scan_id>')
@login_required
def scan_results(scan_id):
    """View the results of a privacy scan."""
    scan = ScanResult.query.get_or_404(scan_id)
    return render_template('scan_results.html', scan=scan)

# Error handling for 404 Not Found
@routes_bp.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    logger.error(f'Page not found: {request.url}')
    return render_template('404.html'), 404

# Error handling for 500 Internal Server Error
@routes_bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f'Server Error: {error}')
    return render_template('500.html'), 500
