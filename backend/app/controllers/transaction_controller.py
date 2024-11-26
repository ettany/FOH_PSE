import random
import datetime
from datetime import datetime, timedelta
from redis import Redis
from rq_scheduler import Scheduler
from flask import Blueprint, jsonify, request, session
import yfinance as yf
from ..db import get_db
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

scheduler = BackgroundScheduler(jobstores={"default": SQLAlchemyJobStore(url="sqlite:///jobs.db")})
scheduler.start()

# Create a Flask blueprint for stock-related routes
transaction_bp = Blueprint('transaction', __name__)

# API route to buy stocks
@transaction_bp.route('/buy', methods=['POST'])
def buy():
    data = request.get_json()
    ticker = data.get("ticker")
    numShares = int(data.get("numShares"))
    session['username']=data.get("username")
    stock = yf.Ticker(ticker)
    stock_info = stock.info

    totalCost = numShares * stock_info.get("currentPrice", 0)
    
    db_conn = get_db()
    id = db_conn.execute(
        "SELECT id FROM user WHERE username = ?", (session['username'],)).fetchone()
    cash = db_conn.execute(
        "SELECT totalCash FROM user WHERE username = ?", (session['username'],)).fetchone()

    if cash is None or id is None:
        return jsonify({"error": "User not found"}), 404

    if totalCost <= cash['totalCash']:
        # Update user's total cash
        db_conn.execute("UPDATE user SET totalCash = totalCash - ? WHERE username = ?",
                        (totalCost, session['username']))
        # Log the buying action
        db_conn.execute("INSERT INTO eventLog (id, eventName, stockBought) VALUES (?, ?, ?)",
                        (id['id'], 'Bought', ticker))
        # Insert stocks into portfolio
        db_conn.execute(
            "INSERT INTO portfolio (ticker, numShares, id) VALUES (?, ?, ?) ON CONFLICT (ticker, id) DO UPDATE SET numShares = numShares + ?",
            (ticker, numShares, id['id'], numShares))
        db_conn.commit()
        return jsonify({"message": "Stock bought successfully", "totalCost": totalCost}), 200
    else:
        return jsonify({"error": "Insufficient funds"}), 400

# API route to sell stocks
@transaction_bp.route('/sell', methods=['POST'])
def sell():
    data = request.get_json()
    ticker = data.get("ticker")
    numShares = int(data.get("numShares"))
    session['username']=data.get("username")
    stock = yf.Ticker(ticker)
    stock_info = stock.info

    totalProfit = numShares * stock_info.get("currentPrice", 0)

    db_conn = get_db()
    session['username']=data.get("username")
    id = db_conn.execute(
        "SELECT id FROM user WHERE username = ?", (session['username'],)).fetchone()
    if id is None:
        return jsonify({"error": "User not found"}), 404

    currentShares = db_conn.execute(
        "SELECT numShares FROM portfolio WHERE id = ? AND ticker = ?", (id['id'], ticker)).fetchone()
    
    if currentShares is None:
        return jsonify({"error": "No shares found in portfolio"}), 404

    if currentShares['numShares'] >= numShares:
        # Update user's total cash
        db_conn.execute(
            "UPDATE user SET totalCash = totalCash + ? WHERE id = ?", (totalProfit, id['id']))
        # Log the selling action
        db_conn.execute(
            "INSERT INTO eventLog (id, eventName, stockBought) VALUES (?, ?, ?)", (id['id'], 'Sold', ticker))
        # Update shares in portfolio
        db_conn.execute(
            "UPDATE portfolio SET numShares = numShares - ? WHERE id = ? AND ticker = ?", (numShares, id['id'], ticker))
        db_conn.commit()
        return jsonify({"message": "Stock sold successfully", "totalProfit": totalProfit}), 200
    else:
        return jsonify({"error": "Not enough shares to sell"}), 400

@transaction_bp.route('/schedule_buy', methods=['POST'])
def schedule_buy():
    data = request.get_json()
    ticker = data.get("ticker")
    numShares = int(data.get("numShares"))
    session['username']=data.get("username")
    schedule_time = data.get("scheduleTime")  # Format: 'YYYY-MM-DD HH:MM:SS'

    scheduler.add_job(
            func=buy,
            trigger="date",
            run_date=schedule_time,
            args=[ticker, numShares, session['username']],
            id=f"{session['username']}-{ticker}-{schedule_time}",  # Unique job ID
            replace_existing=True
        )
def buy(ticker, numShares):
    stock = yf.Ticker(ticker)

    stock_info = stock.info

    totalCost = numShares * stock_info.get("currentPrice", 0)
    
    db_conn = get_db()
    id = db_conn.execute(
        "SELECT id FROM user WHERE username = ?", (session['username'],)).fetchone()
    cash = db_conn.execute(
        "SELECT totalCash FROM user WHERE username = ?", (session['username'],)).fetchone()

    if cash is None or id is None:
        return jsonify({"error": "User not found"}), 404

    if totalCost <= cash['totalCash']:
        # Update user's total cash
        db_conn.execute("UPDATE user SET totalCash = totalCash - ? WHERE username = ?",
                        (totalCost, session['username']))
        # Log the buying action
        db_conn.execute("INSERT INTO eventLog (id, eventName, stockBought) VALUES (?, ?, ?)",
                        (id['id'], 'Bought', ticker))
        # Insert stocks into portfolio
        db_conn.execute(
            "INSERT INTO portfolio (ticker, numShares, id) VALUES (?, ?, ?) ON CONFLICT (ticker, id) DO UPDATE SET numShares = numShares + ?",
            (ticker, numShares, id['id'], numShares))
        db_conn.commit()
        return jsonify({"message": "Stock bought successfully", "totalCost": totalCost}), 200
    else:
        return jsonify({"error": "Insufficient funds"}), 400
    
@transaction_bp.route('/schedule_sell', methods=['POST'])
def schedule_sell():
    data = request.get_json()
    ticker = data.get("ticker")
    numShares = int(data.get("numShares"))
    session['username']=data.get("username")
    schedule_time = data.get("scheduleTime")  # Format: 'YYYY-MM-DD HH:MM:SS'

    scheduler.add_job(
            func=sell,
            trigger="date",
            run_date=schedule_time,
            args=[ticker, numShares, session['username']],
            id=f"{session['username']}-{ticker}-{schedule_time}",  # Unique job ID
            replace_existing=True
        )
def sell(ticker, numShares):
    stock = yf.Ticker(ticker)
    stock_info = stock.info

    totalProfit = numShares * stock_info.get("currentPrice", 0)

    db_conn = get_db()
    id = db_conn.execute(
        "SELECT id FROM user WHERE username = ?", (session['username'],)).fetchone()
    if id is None:
        return jsonify({"error": "User not found"}), 404

    currentShares = db_conn.execute(
        "SELECT numShares FROM portfolio WHERE id = ? AND ticker = ?", (id['id'], ticker)).fetchone()
    
    if currentShares is None:
        return jsonify({"error": "No shares found in portfolio"}), 404

    if currentShares['numShares'] >= numShares:
        # Update user's total cash
        db_conn.execute(
            "UPDATE user SET totalCash = totalCash + ? WHERE id = ?", (totalProfit, id['id']))
        # Log the selling action
        db_conn.execute(
            "INSERT INTO eventLog (id, eventName, stockBought) VALUES (?, ?, ?)", (id['id'], 'Sold', ticker))
        # Update shares in portfolio
        db_conn.execute(
            "UPDATE portfolio SET numShares = numShares - ? WHERE id = ? AND ticker = ?", (numShares, id['id'], ticker))
        db_conn.commit()
        return jsonify({"message": "Stock sold successfully", "totalProfit": totalProfit}), 200
    else:
        return jsonify({"error": "Not enough shares to sell"}), 400
