from flask import Blueprint, jsonify, request, session, render_template
import datetime
from ..db import get_db

log_bp = Blueprint('log', __name__)

@log_bp.route('/stocklist', methods=['GET'])
def getLog():
    data = request.get_json()
    session['username'] = data.get("username")
    db_conn = get_db()
    
    # Fetch user ID from username
    user_id = db_conn.execute(
        "SELECT id FROM user WHERE username = ?", (session['username'],)
    ).fetchone()
    
    if user_id is None:
        return jsonify({"error": "User not found"}), 404
    
    # Fetch log entries related to the user
    log_entries = db_conn.execute(
        "SELECT id, eventName, stockBought, stockSold, date FROM eventLog WHERE user_id = ?", (user_id['id'],)
    ).fetchall()
    
    # Convert entries to dictionaries for easy access in the template
    log_entries = [dict(entry) for entry in log_entries]
    
    return render_template('log.html', log_entries=log_entries)