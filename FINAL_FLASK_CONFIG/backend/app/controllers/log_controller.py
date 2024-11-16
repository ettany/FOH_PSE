from flask import Blueprint, jsonify, request, session, render_template
import datetime
from ..db import get_db

log_bp = Blueprint('log', __name__)

@log_bp.route('/entries', methods=['GET'])
def get_log_entries():
    try:
        print("Fetching log entries...")  # Debugging print statement
        db_conn = get_db()  # Get database connection
        cursor = db_conn.execute("SELECT id, eventName, stockSold, stockBought, date FROM eventLog")
        log_entries = [
            {
                'id': row['id'],
                'eventName': row['eventName'],
                'stockSold': row['stockSold'],
                'stockBought': row['stockBought'],
                'date': row['date']
            }
            for row in cursor.fetchall()
        ]
        return jsonify(log_entries), 200
    except Exception as e:
        print(f"Error fetching log entries: {e}")
        return jsonify({"error": "Failed to fetch log entries"}), 500