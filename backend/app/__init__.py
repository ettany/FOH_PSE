from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import timedelta
from flask_apscheduler import APScheduler
from flask_swagger_ui import get_swaggerui_blueprint


scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config['SCHEDULER_API_ENABLED'] = True
    app.config['APSCHEDULER_TIMEZONE'] = 'UTC'  # Set appropriate timezone
    # Load environment variables from .env file
    load_dotenv()

    # Enable CORS for requests from the frontend on port 5001
    CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5001"])
    
    # App configurations
    app.config['DATABASE'] = 'database.db'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

    # Initialize database
    from .db import init_app
    init_app(app)

    # Register blueprints
    from .controllers.user_controller import user_bp
    from .controllers.log_controller import log_bp
    from .controllers.stock_controller import stock_bp
    from .controllers.transaction_controller import transaction_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(log_bp, url_prefix='/api/log')
    app.register_blueprint(stock_bp, url_prefix='/api/stock')
    app.register_blueprint(transaction_bp, url_prefix='/api/transaction')
    scheduler.init_app(app)  
    scheduler.start()

    # Swagger UI setup
    SWAGGER_URL = '/api/docs'
    API_URL = '/swagger.json'
    swaggerui_bp = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swaggerui_bp)

    # Swagger JSON route
    @app.route('/swagger.json')
    def swagger_spec():
        from flask_swagger import swagger
        with app.app_context():
            return jsonify(swagger(app))

    return app