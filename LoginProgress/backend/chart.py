import random
import datetime
from flask import Blueprint, jsonify
import yfinance as yf
import os

# Create a Flask blueprint for stock-related routes
stockChart_blueprint = Blueprint("chart", __name__)


def fetch_real_stock_data(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(period="30d")  # Get stock data (last 30 days)

    dates = hist.index.to_list()
    prices = hist["Close"].to_list()

    return dates, prices


# def fetch_stock_data(stock_symbol):
#     stock = yf.Ticker(stock_symbol)
#     stock_info = stock.history(period="1mo")
#     dates = stock_info.index.strftime("%Y-%m-%d").tolist()
#     prices = stock_info["Close"].tolist()

#     return {
#         "ticker": stock_symbol,
#         "dates": dates,
#         "prices": prices,
#         "name": stock.info.get("shortName"),
#         "price": stock.info.get("currentPrice"),
#     }


# API route to return real stock data
@stockChart_blueprint.route("/stock_chart", methods=["GET"])
def stock_data():

    dates, prices = fetch_real_stock_data("AAPL")

    return jsonify(
        {"dates": [date.strftime("%Y-%m-%d") for date in dates], "prices": prices}
    )


@stockChart_blueprint.route("/top_stocks", methods=["GET"])
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
    top_stocks = dict(
        sorted(stocks.items(), key=lambda item: item[1]["price"], reverse=True)[:5]
    )

    return jsonify(top_stocks)
