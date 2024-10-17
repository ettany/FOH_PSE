from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/log')  # Adding the log route
    def log():
        return render_template('log.html')

    @app.route('/logout')  # Adding the logout route
    def logout():
        return render_template('logout.html')

    @app.route('/register')  # Adding the register route
    def register():
        return render_template('register.html')

    @app.route('/trade')  # Adding the trade route
    def trade():
        return render_template('trade.html')

    return app