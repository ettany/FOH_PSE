from flask import Blueprint, request, jsonify, flash, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from ..db import get_db

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()  # Get JSON data from the request
    username = data.get('username')
    password = data.get('password')

    # Check the credentials against the database
    try:
        db_conn = get_db()
        user = db_conn.execute(
            "SELECT * FROM user WHERE username = ?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user['password'], password):
            session["username"] = username
            session["totalCash"] = user["totalCash"]
            session.permanent = True  # Make session permanent if desired
            print("Session set: ", session)
            if username == "administration":

                return jsonify({"message": "Admin login successful!", "user": username}), 200
            else:
                return jsonify({"message": "User login successful!", "user": username, "totalCash": user["totalCash"]}), 200
        else:
            return jsonify({"error": "Invalid username or password!"}), 401

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database connection error"}), 500

@user_bp.route('/register', methods=['POST'])
def register():
    if request.method == "POST":
        data = request.get_json()  # Get JSON data from the request
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"error": "Username and password are required."}), 400
        # Check if the username already exists
        db_conn = get_db()
        existing_user = db_conn.execute(
            "SELECT * FROM user WHERE username = ?",
            (username,)
        ).fetchone()
        if existing_user:
            return jsonify({"error": "Username already taken"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        try:
            # Insert user into the database
            db_conn.execute(
                "INSERT INTO user (username, password, totalCash) VALUES (?, ?, ?)",
                (username, hashed_password, 100000)
            )
            db_conn.commit()
            return jsonify({"message": "User registered successfully!"}), 201
        except Exception:
            return jsonify({"error": "Registration failed. Please try again."}), 500

@user_bp.route('/index', methods=['GET'])
def index():
    print("Session at index:", session)  # Check current session state
    print("Check Username", session.get("username"))
    username = session.get("username")
    total_cash = session.get("totalCash")

    if not username:
        return jsonify({"error": "User not logged in."}), 401

    return jsonify({"username": username, "totalCash": total_cash}), 200  # Return JSON data

@user_bp.route('/admin', methods=['GET'])
def admin():
    username = session.get("username")
    return jsonify({"message": "Login successful!", 'username': username}),200
