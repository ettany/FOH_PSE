from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from ..db import *

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check the credentials against the database
        db_conn = get_db()
        user = db_conn.execute(
            "SELECT * FROM user WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()

    if user and check_password_hash(user['password'], password):
        return jsonify({"message": "Login successful!", "user": user['username']}), 200
    return jsonify({"error": "Invalid username or password!"}), 401

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    total_cash = data.get('totalCash', 0)

    db = get_db()
    hashed_password = generate_password_hash(password)
    try:
        db.execute("INSERT INTO user (username, password, totalCash) VALUES (?, ?, ?)",
                   (username, hashed_password, total_cash))
        db.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
