import os
from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf
import db
from flask import Flask, render_template, redirect, url_for, session, flash
from chart import stockChart_blueprint
from flask_cors import CORS

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "..", "frontend", "templates"
        ),
        static_folder=os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "..", "frontend", "static"
        ),
    )

    # Set up the path to the database
    app.config["DATABASE"] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "database.db"
    )
    # Enable CORS for all routes
    CORS(app)

    app.register_blueprint(stockChart_blueprint)

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


@app.route("/trade")
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


@app.route("/buy", methods=["POST"])
def buy():

    ticker = request.form["ticker"]
    numShares = int(request.form["numShares"])

    stock = yf.Ticker(ticker)
    stock_info = stock.info

    totalCost = numShares * stock_info.get("currentPrice")

    db_conn = db.get_db()
    id = db_conn.execute(
        "SELECT id FROM user WHERE username = ?", (session['username'])).fetchone()
    cash = db_conn.execute(
        "SELECT totalCash FROM user WHERE username = ?", (session['username'])).fetchone()
    if (totalCost <= cash['totalCash']):
        # Set total cash to be lower
        db_conn.execute("UPDATE user SET totalCash = totalCash - ? WHERE username = ?",
                        (totalCost, session['username']))
        # insert buying action into event log
        db_conn.execute("INSERT INTO eventLog (id, eventName, stockBought) VALUES (?, ?, ?)",
                        (id['id'], 'Bought', ticker))
        # insert stocks into portfolio
        db_conn.execute(
            "INSERT INTO portfolio (ticker, numShares, id) VALUES(?,?,?)", (ticker, numShares, id['id']))
        return redirect(url_for("trade"))
    else:
        "Error"


@app.route("/sell", methods=["POST"])
def sell():

    ticker = request.form["ticker"]
    numShares = int(request.form["numShares"])

    stock = yf.Ticker(ticker)
    stock_info = stock.info

    totalProfit = numShares * stock_info.get("currentPrice")

    db_conn = db.get_db()

    id = db_conn.execute(
        "SELECT id FROM user WHERE username = ?", (session['username'])).fetchone()

    currentShares = db_conn.execute(
        "SELECT numShares FROM portfolio WHERE id = ? AND ticker = ?", (id, ticker))

    if (currentShares['numShares'] >= numShares):
        # Set total cash to be higher
        db_conn.execute(
            "UPDATE user SET totalCash = totalCash + ? WHERE id = ?", (totalProfit, id['id']))
        # insert selling action into event log
        db_conn.execute(
            "INSERT INTO eventLog (id, eventName, stockBought) VALUES (?, ?, ?)", (id['id'], 'Sold', ticker))
        # remove number of shares from portfolio table -- maybe readjust to only print stocks with a number of shares greater than zero?
        db_conn.execute(
            "UPDATE portfolio SET numShares = numShares - ? WHERE id = ? AND ticker = ?", (numShares, id['id'], ticker))
        return redirect(url_for("trade"))
    else:
        "Error"


@app.route("/admin")
def admin():
    username = session.get("username")
    return render_template("admin.html", username=username)


@app.route("/visualization")
def visualization():
    return render_template("visualization.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")


if __name__ == "__main__":
    app.run(debug=True)
