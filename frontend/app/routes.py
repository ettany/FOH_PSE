from flask import Blueprint, render_template
import requests

main = Blueprint('main', __name__)

# @main.route('/')
# def home():
#     # Fetch stocks from backend API
#     response = requests.get('http://localhost:5000/api/stocks')
#     stocks = response.json()
#     return render_template('register.html', stocks=stocks)
