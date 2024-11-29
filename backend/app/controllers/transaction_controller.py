import random
import datetime
from datetime import datetime, timedelta
from redis import Redis
from rq_scheduler import Scheduler
from flask import Blueprint, app, jsonify, request, session
import yfinance as yf
from ..db import get_db
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from app import scheduler  # Import directly from app/__init__.py
from flask import current_app


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


@transaction_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    username = session.get('username')
    if not username:
        return jsonify({"error": "User not logged in"}), 401

    db_conn = get_db()
    user_id = db_conn.execute(
        "SELECT id FROM user WHERE username = ?", (username,)).fetchone()

    if not user_id:
        return jsonify({"error": "User not found"}), 404

    portfolio = db_conn.execute(
        "SELECT ticker, numShares FROM portfolio WHERE id = ?", (user_id['id'],)).fetchall()

    response_data = []
    for stock in portfolio:
        ticker = stock['ticker']
        numShares = stock['numShares']
        stock_info = yf.Ticker(ticker).info
        current_price = stock_info.get("currentPrice", 0)
        previous_close = stock_info.get("regularMarketPreviousClose", 0)

        price_change = current_price - previous_close
        price_change_percent = (price_change / previous_close) * 100 if previous_close else 0

        response_data.append({
            "ticker": ticker,
            "numShares": numShares,
            "currentPrice": current_price,
            "price_change": price_change,
            "price_change_percent": price_change_percent
        })

    return jsonify(response_data), 200
@transaction_bp.route('/schedule_buy', methods=['POST'])
def schedule_buy():
    data = request.get_json()
    ticker = data.get("ticker")
    numShares = int(data.get("numShares"))
    username = data.get("username")
    schedule_time = data.get("scheduleTime")  
    schedule_datetime = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M")

    try:
        scheduler.add_job(
                func=buy,
                trigger="date",
                run_date=schedule_datetime,
            kwargs={'app': current_app._get_current_object(), 'ticker': ticker, 'numShares': numShares, 'username': username},
                id=f"{username}-{ticker}-{schedule_time}",  
                replace_existing=True
            )
        print(f"Job scheduled: {username}-{ticker} at {schedule_time}")

        return jsonify({"message": "Stock buy scheduled successfully", "schedule_time": schedule_time}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
def buy(app, ticker, numShares, username):
    with app.app_context(): 
        try:
            print(f"Executing buy job: {ticker}, {numShares}, {username}")
            stock = yf.Ticker(ticker)
            stock_info = stock.info

            totalCost = numShares * stock_info.get("currentPrice", 0)
            db_conn = get_db()
            id = db_conn.execute(
                "SELECT id FROM user WHERE username = ?", (username,)).fetchone()
            cash = db_conn.execute(
                "SELECT totalCash FROM user WHERE username = ?", (username,)).fetchone()

            if cash is None or id is None:
                print("User not found")
                return {"error": "User not found"}

            if totalCost <= cash['totalCash']:
                # Update user's total cash
                db_conn.execute("UPDATE user SET totalCash = totalCash - ? WHERE username = ?",
                                (totalCost, username))
                # Log the buying action
                db_conn.execute("INSERT INTO eventLog (id, eventName, stockBought) VALUES (?, ?, ?)",
                                (id['id'], 'Bought', ticker))
                # Insert stocks into portfolio
                db_conn.execute(
                    "INSERT INTO portfolio (ticker, numShares, id) VALUES (?, ?, ?) ON CONFLICT (ticker, id) DO UPDATE SET numShares = numShares + ?",
                    (ticker, numShares, id['id'], numShares))
                db_conn.commit()
                print(f"Stock bought successfully: {ticker} by {username}")
                return {"message": "Stock bought successfully", "totalCost": totalCost}
            else:
                print("Insufficient funds")
                return {"error": "Insufficient funds"}
        except Exception as e:
            print(f"Error in scheduled job: {str(e)}")
@transaction_bp.route('/schedule_sell', methods=['POST'])
def schedule_sell():
    data = request.get_json()
    ticker = data.get("ticker")
    numShares = int(data.get("numShares"))
    username = data.get("username")
    schedule_time = data.get("scheduleTime") 

    scheduler.add_job(
        func=sell,
        trigger="date",
        run_date=schedule_time,
            kwargs={'app': current_app._get_current_object(), 'ticker': ticker, 'numShares': numShares, 'username': username},
        id=f"{username}-{ticker}-{schedule_time}", 
        replace_existing=True
    )
    print(f"Job scheduled: {username}-{ticker} at {schedule_time}")

    return jsonify({"message": f"Sell job scheduled for {schedule_time}"}), 200
def sell(app, ticker, numShares, username):
    with app.app_context(): 
        stock = yf.Ticker(ticker)
        stock_info = stock.info

        totalProfit = numShares * stock_info.get("currentPrice", 0)
        db_conn = get_db()
        id = db_conn.execute(
                "SELECT id FROM user WHERE username = ?", (username,)).fetchone()
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

