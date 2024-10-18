from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['DATABASE'] = 'database.db'
    app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your secret key

    from .db import init_app
    init_app(app)

    from .controllers.user_controller import user_bp
    from .controllers.stock_controller import stock_bp
    
    # Register blueprints with their respective prefixes
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(stock_bp, url_prefix='/api/stocks')  # One registration for stock_bp

    return app
