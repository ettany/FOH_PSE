import random
import datetime
from flask import Blueprint, jsonify
import yfinance as yf
import os
# Create a Flask blueprint for stock-related routes
stockChart_blueprint = Blueprint('chart', __name__)

# Function to generate random stock data
def generate_stock_data():
    dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(30)]
    prices = [random.randint(100, 200) for _ in range(30)]
    return dates[::-1], prices[::-1]

# API route to return stock data as JSON
@stockChart_blueprint.route('/stock_chart', methods=['GET'])
def stock_data():
    dates, prices = generate_stock_data()
    return jsonify({
        "dates": [date.strftime('%Y-%m-%d') for date in dates],
        "prices": prices
    })

@stockChart_blueprint.route('/top_stocks', methods=['GET'])
def get_top_stocks():
    stocks = {}
    tickers_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "logs", "tickers.txt"
    )

    with open(tickers_file_path, "r") as file:
        tickers = [line.strip() for line in file.readlines()]

    # Fetch stock prices and store them in a dictionary
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        current_price = stock_info.get("currentPrice")

        # Only add the stock if the current price is valid
        if current_price is not None:
            stocks[ticker] = {
                "name": stock_info.get("shortName"),
                "price": current_price,
            }

    # Sort stocks by price in descending order and get the top 5
    top_stocks = dict(sorted(stocks.items(), key=lambda item: item[1]['price'], reverse=True)[:5])

    return jsonify(top_stocks)