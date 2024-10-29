from flask import Flask, session
from flask_cors import CORS
import os
from dotenv import load_dotenv  # Import load_dotenv
from .db import init_app  # Make sure to import the init_app function from db.py
from datetime import timedelta
from flask_session import Session
def create_app():
    app = Flask(__name__)

    # Load environment variables from .env file
    load_dotenv()

    # Enable CORS for all routes
    CORS(app)  # Allow credentials to be sent with requests

    # Enable CORS for requests from the frontend on port 5001
    CORS(app, resources={r"/api/*": {"origins": os.getenv('UI_URL')}}, supports_credentials=True)
    
        # Set up the path to the database
    app.config["DATABASE"] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "database.db"
    )
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  
    app.config['DEBUG'] = True
    app.config['ENV'] = 'development'  # This also sets the environment to development
    # app.config['SESSION_COOKIE_SECURE'] = False  # Change to True if using HTTPS
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True  # Session will expire when the browser closes
    # Configure session cookie properties
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cookies to be sent with cross-site requests
    app.config['SESSION_COOKIE_SECURE'] = True  # Ensures cookies are only sent over HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.permanent_session_lifetime = timedelta(days=7)  # Set how long sessions last
    Session(app)
    # Initialize the database setup
    init_app(app)  # This adds the init-db command to the app

    from .controllers.user_controller import user_bp
    from .controllers.stock_controller import stock_bp
    from .controllers.transaction_controller import transaction_bp
    # Register blueprints with their respective prefixes
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(stock_bp, url_prefix='/api/stock')  # One registration for stock_bp
    app.register_blueprint(transaction_bp, url_prefix='/api/transaction')  # One registration for transaction
    return app
