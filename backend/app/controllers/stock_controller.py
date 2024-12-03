import os
from flask import Blueprint, jsonify, request
import yfinance as yf
import pandas as pd

stock_bp = Blueprint('stock', __name__)


@stock_bp.route('/stocklist', methods=['GET'])
def get_stocks():
    """
    Get a list of stocks with their basic details
    ---
    tags:
      - Stocks
    summary: Retrieve a list of stocks
    description: Fetch a predefined list of stocks and their basic details (name and current price).
    responses:
      200:
        description: A JSON object containing stock details
        content:
          application/json:
            schema:
              type: object
              additionalProperties:
                type: object
                properties:
                  name:
                    type: string
                    description: The stock's short name
                  price:
                    type: number
                    description: The stock's current price
      500:
        description: Internal server error
    """
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

    return jsonify(stocks)


@stock_bp.route('/stockSearch', methods=['POST'])
def searchStock():
    """
    Search for a stock by ticker symbol
    ---
    tags:
      - Stocks
    summary: Search for a specific stock
    description: Search for a stock by its ticker symbol and retrieve its name, current price, and historical data for the last 30 days.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              stock_search:
                type: string
                description: The ticker symbol of the stock to search for
                example: AAPL
    responses:
      200:
        description: A JSON object containing stock details and historical data
        content:
          application/json:
            schema:
              type: object
              properties:
                stock:
                  type: object
                  properties:
                    ticker:
                      type: string
                      description: The stock's ticker symbol
                    name:
                      type: string
                      description: The stock's short name
                    price:
                      type: number
                      description: The stock's current price
                history:
                  type: object
                  additionalProperties:
                    type: number
                  description: A mapping of dates to closing prices for the last 30 days
      404:
        description: Stock not found or data unavailable
      500:
        description: Internal server error
    """
    searched_stock = None

    if request.method == "POST":
        data = request.get_json()
        search_ticker = data.get("stock_search").upper()
        stock = yf.Ticker(search_ticker)
        stock_info = stock.info

        if "shortName" in stock_info and "currentPrice" in stock_info:
            searched_stock = {
                "ticker": search_ticker,
                "name": stock_info["shortName"],
                "price": stock_info["currentPrice"],
            }

            # Get historical data for the last 5 days
            hist = stock.history(period="30d")

            # Convert the index (Timestamps) to strings and format the historical prices
            history_data = hist['Close'].to_dict()
            history_data = {str(date.date()): price for date,
                            price in history_data.items()}

            return jsonify({
                "stock": searched_stock,
                "history": history_data  # Use the modified history data
            })

        return jsonify({"error": "Stock not found or data unavailable."}), 404

    return jsonify({"error": "Invalid request."}), 400
