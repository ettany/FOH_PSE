import os
from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf
import db
from flask import Flask, render_template, redirect, url_for, session, flash


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
    db.init_app(app)

    return app


app = create_app()

app.secret_key = "!@#$%"


@app.route("/")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the username already exists
        db_conn = db.get_db()
        existing_user = db_conn.execute(
            "SELECT * FROM user WHERE username = ?",
            (username,),
        ).fetchone()

        if existing_user:
            flash("Username already taken. Please choose a different one.")
            return redirect(url_for("register"))

        # Insert user into the database
        db_conn.execute(
            "INSERT INTO user (username, password, totalCash) VALUES (?, ?, ?)",
            (username, password, 100000),
        )
        db_conn.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/index")
def index():
    username = session.get("username")
    totalCash = session.get("totalCash")
    return render_template("index.html", username=username, totalCash=totalCash)


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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check the credentials against the database
        try:
            db_conn = db.get_db()
            user = db_conn.execute(
                "SELECT * FROM user WHERE username = ? AND password = ?",
                (username, password),
            ).fetchone()

            if user:
                session["username"] = username
                if username == "administration":
                    return redirect(url_for("admin"))
                else:
                    session["totalCash"] = user["totalCash"]
                    return redirect(url_for("index"))
            else:
                flash("Invalid Credentials.")
                return redirect(url_for("login"))

        except Exception as e:
            print(f"Error: {e}")
            return "Database connection error"

    return render_template("login.html")


@app.route("/admin")
def admin():
    username = session.get("username")
    return render_template("admin.html", username=username)


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")


if __name__ == "__main__":
    app.run(debug=True)
