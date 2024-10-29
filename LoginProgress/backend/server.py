import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import yfinance as yf
import db
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "templates"
        ),
        static_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "static"
        ),
    )

    # Set up the path to the database
    app.config["DATABASE"] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "database.db"
    )

    # Initialize the database commands
    db.init_app(app)  # Make sure this line is uncommented and included

    return app



app = create_app()
app.config['DATABASE'] = 'database.db'
# Configure Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'  # Redirect to login if not authenticated
login_manager.init_app(app)

app.secret_key = '!@#$%'  # Consider using a more secure key for production


# Class definition
class User(UserMixin):
    def __init__(self, id, username, totalCash, password_hash=None):
        self.id = id
        self.username = username
        self.totalCash = totalCash
        self.password_hash = password_hash  # Optional

    @staticmethod
    def get_user(username):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, totalCash FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return User(id=user[0], username=user[1], password_hash=user[2], totalCash=user[3])
        return None



# Flask-Login callback to load user from session
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(app.config['DATABASE'])  # Use app.config for DB path
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, totalCash FROM user WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], totalCash=user[2])
    return None


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():

    username = ""
    password = ""

    if request.args.get("clear"):
        # Reset form fields
        username = ""
        password = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.get_user(username)
        if user and check_password_hash(user.password_hash, password):  # Ensure user.password_hash is accessed correctly
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('portfolio'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template("login.html", username=username, password=password)

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Save the user to the database
        hashed_password = generate_password_hash(password)

        db_conn = db.get_db()
        try:
            db_conn.execute(
                "INSERT INTO user (username, password_hash, totalCash) VALUES (?, ?, ?)",
                (username, hashed_password, 10000.0)
            )
            db_conn.commit()
            flash('Registration successful! Please log in.', 'success')
            # Redirect to login page after registration
            return redirect(url_for("login", clear=True))  # Add 'clear' query param
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'error')

    return render_template('register.html')


@app.route("/index1", endpoint="portfolio")
@login_required
def index1():
    username = current_user.username  # Get username from current_user
    totalCash = current_user.totalCash  # Get totalCash from current_user
    return render_template("index1.html", username=username, totalCash=totalCash)


@app.route("/trade", methods=["GET", "POST"])
def trade():
    stocks = {}
    tickers_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "logs", "tickers.txt"
    )

    with open(tickers_file_path, "r") as file:
        tickers = [line.strip() for line in file.readlines()]

    for ticker in tickers[:5]:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        stocks[ticker] = {
            "name": stock_info.get("shortName"),
            "price": stock_info.get("currentPrice"),
        }

    searched_stock = None

    # Searching for a specific stock
    if request.method == "POST":
        search_ticker = request.form["stock_search"].upper()
        stock = yf.Ticker(search_ticker)
        stock_info = stock.info

        # Check if the stock data exists and is valid
        if "shortName" in stock_info and "currentPrice" in stock_info:
            searched_stock = {
                "ticker": search_ticker,
                "name": stock_info["shortName"],
                "price": stock_info["currentPrice"],
            }

    return render_template("trade.html", stocks=stocks, searched_stock=searched_stock)


@app.route("/log")
def log():
    return render_template("log.html")

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return f'Welcome, {current_user.username}! Your total cash is {current_user.totalCash}.'

@app.route("/admin")
def admin():
    username = session.get("username")
    return render_template("admin.html", username=username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
