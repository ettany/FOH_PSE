import os
from flask import Blueprint, jsonify, request
import yfinance as yf

from yahooquery import Screener
stock_bp = Blueprint('stock', __name__)

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')  # Load your API key from environment variables

@stock_bp.route('/', methods=['GET'])
def get_stocks():
    stocks = {}
    tickers_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),"..", "logs", "tickers.txt"
    )

    with open(tickers_file_path, "r") as file:
        tickers = [line.strip() for line in file.readlines()]

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        stocks[ticker] = {
            "name": stock_info.get("shortName"),
            "price": stock_info.get("currentPrice"),
        }

    return jsonify(stocks)
