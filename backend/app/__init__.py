from flask import Flask
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv  # Import load_dotenv
def create_app():
    app = Flask(__name__)

    # Load environment variables from .env file
    load_dotenv()

    # Enable CORS for requests from the frontend on port 5001
    # CORS(app, resources={r"/api/*": {"origins": os.getenv('UI_URL')}})
    CORS(app, resources={r"/api/*": {"origins": "*"}}, support_credentials=True)
    
    
    app.config['DATABASE'] = 'database.db'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  

    from .db import init_app
    init_app(app)

    from .controllers.user_controller import user_bp
    from .controllers.stock_controller import stock_bp
    from .controllers.transaction_controller import transaction_bp
    # Register blueprints with their respective prefixes
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(stock_bp, url_prefix='/api/stock')  # One registration for stock_bp
    app.register_blueprint(transaction_bp, url_prefix='/api/transaction')  # One registration for transaction
    return app
