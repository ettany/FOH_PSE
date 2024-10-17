from flask import Flask, render_template
import yfinance as yf

from yahooquery import Screener

app = Flask(__name__)

@app.route('/')

# Trade route
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/trade')
def trade():
    stocks = {}
    # Fetch stock data 
    with open('tickers.txt', 'r') as file:
        tickers = [line.strip() for line in file.readlines()]

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        stocks[ticker] = {
            "name": stock_info.get("shortName"),
            "price": stock_info.get("currentPrice")
        }

    return render_template("trade.html", stocks=stocks)

# Log route
@app.route('/log')
def log():
    return render_template("log.html")

@app.route('/logout')
def logout():
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(debug=True)

from . import db
db.init_app(app)


