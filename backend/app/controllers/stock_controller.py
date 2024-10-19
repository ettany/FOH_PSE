import os
import requests
from flask import Blueprint, jsonify, request

stock_bp = Blueprint('stock', __name__)

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')  # Load your API key from environment variables

@stock_bp.route('/', methods=['GET'])
def get_stocks():
    # symbols = request.args.get('symbols')  # Fetch symbols from query parameters
    symbols = request.args.get('symbols', 'AAPL,GOOGL,TSLA')  # Default to these symbols if none are provided
    if not symbols:
        return jsonify({'error': 'No stock symbols provided'}), 400
    
    symbols_list = symbols.split(',')  # Split symbols by comma if multiple are provided
    stocks_data = {}
    
    for symbol in symbols_list:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}'
        response = requests.get(url)
        data = response.json()
        
        if 'Time Series (5min)' in data:
            latest_time = next(iter(data['Time Series (5min)']))
            stocks_data[symbol] = {
                'name': symbol,  # Modify this to get actual company names if 
                'price': data['Time Series (5min)'][latest_time]['1. open']  # Fetch the latest price
            }
        else:
            stocks_data[symbol] = {'name': symbol, 'price': 'N/A'}  # Handle errors gracefully

    return jsonify(stocks_data)
