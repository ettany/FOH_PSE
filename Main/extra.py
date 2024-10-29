from flask import Flask, render_template
import yfinance as yf
import os

from yahooquery import Screener

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'static'))

@app.route('/')

# Trade route
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/trade')
def trade():
    stocks = {}
    
    tickers_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs', 'tickers.txt')

    with open(tickers_file_path, 'r') as file:
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


