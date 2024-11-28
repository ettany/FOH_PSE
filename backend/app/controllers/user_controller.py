<<<<<<< HEAD
from flask import Blueprint, request, jsonify, flash, session, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from ..db import get_db
import datetime
=======
import requests
from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from ..db import get_db
import datetime
import os
>>>>>>> origin/Final-Flask

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
<<<<<<< HEAD

    data = request.get_json()  # Get JSON data from the request
    username = data.get('username')
    password = data.get('password')
=======
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    captcha_response = data.get('captcha_response')  # Get CAPTCHA response from the front-end
    
    # Verify CAPTCHA response with Google
    secret_key = os.getenv('RECAPTCHA_SECRET_KEY')  # Replace with your actual secret key
    print('Secret Key: ', secret_key)
    captcha_verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    captcha_result = requests.post(captcha_verify_url, data={
        'secret': secret_key,
        'response': captcha_response
    })
    result = captcha_result.json()

    # If CAPTCHA verification fails, return an error
    if not result.get('success'):
        return jsonify({"error": "CAPTCHA verification failed."}), 400
>>>>>>> origin/Final-Flask

    # Check the credentials against the database
    try:
        db_conn = get_db()
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = db_conn.execute(
            "SELECT * FROM user WHERE username = ?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user['password'], password):
            session["username"] = username
            session["totalCash"] = user["totalCash"]
            session["user_id"] = user["id"]
            session.permanent = True  # Make session permanent if desired
            try:
                db_conn.execute(
<<<<<<< HEAD
                "INSERT INTO eventLog (id, eventName, stockSold, stockBought, date) VALUES (?, ?, NULL, NULL, ?)",
                (user["id"], "Logged on", timestamp)
                )
                db_conn.commit()

=======
                    "INSERT INTO eventLog (id, eventName, stockSold, stockBought, date) VALUES (?, ?, NULL, NULL, ?)",
                    (user["id"], "Logged on", timestamp)
                )
                db_conn.commit()
>>>>>>> origin/Final-Flask
            except Exception:
                print("Error adding login to eventLog")
                return jsonify({"error": "Error adding login to eventLog. Please try again."}), 500
            
            print("Session set: ", session)
            if username == "administration":
<<<<<<< HEAD

=======
>>>>>>> origin/Final-Flask
                return jsonify({"message": "Admin login successful!", "user": username}), 200
            else:
                return jsonify({"message": "User login successful!", "user": username, "totalCash": user["totalCash"], "user_id": user["id"]}), 200
        else:
            return jsonify({"error": "Invalid username or password!"}), 401

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database connection error"}), 500

@user_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Retrieve user_id from session before clearing it
        print("Session: ", session)
        user_id = session.get("user_id")
        print(f"Logging out user with ID: {user_id}")

        if not user_id:
            return jsonify({"error": "No user is currently logged in!"}), 400

        # Get the current timestamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Log the logout event
        db_conn = get_db()
        try:
            db_conn.execute(
                "INSERT INTO eventLog (id, eventName, stockSold, stockBought, date) VALUES (?, ?, NULL, NULL, ?)",
                (user_id, "Logged out", timestamp)
            )
            db_conn.commit()
        except Exception as e:
            print(f"Error adding logout to eventLog: {e}")
            return jsonify({"error": "Error adding logout to eventLog. Please try again."}), 500

        # Clear the session
        session.clear()

        return jsonify({"message": "User logged out successfully!"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500



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

@user_bp.route('/index', methods=['POST'])
def index():
    print("Session at index:", session)  # Check current session state
    # Get the username from the request body
    data = request.get_json()
    username = data.get("username")
    print("Check Username", username)

    if not username:
        return jsonify({"error": "User not authenticated"}), 403
    else:
        try:
            # Get the user's balance from the database
            db_conn = get_db()
            cursor = db_conn.execute("SELECT totalCash FROM user WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user:
                return jsonify({"totalCash": user["totalCash"]}), 200
            else:
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "User not authenticated"}), 403

@user_bp.route('/admin', methods=['GET'])
def admin():
    username = session.get("username")
    return jsonify({"message": "Login successful!", 'username': username}),200

@user_bp.route('/create_user', methods=['POST'])
def create_user():
    username = request.json.get("username")
    password = request.json.get("password")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    db_conn = get_db()
    existing_user = db_conn.execute(
        "SELECT * FROM user WHERE username = ?",
        (username,)
    ).fetchone()

    if existing_user:
        return jsonify({"error": "Username already taken"}), 409
    
    hashed_password = generate_password_hash(password)  # Hash the password for security
    db_conn.execute(
        "INSERT INTO user (username, password, totalCash) VALUES (?, ?, ?)",
        (username, hashed_password, 100000),
    )
    db_conn.commit()
    
    return jsonify({"message": "User created successfully"}), 201


@user_bp.route('/delete_user', methods=['DELETE'])
def delete_user():
    username_to_delete = request.json.get("username")
    
    if not username_to_delete or username_to_delete == 'administration':
        return jsonify({"error": "Invalid operation"}), 400
    
    db_conn = get_db()
    db_conn.execute(
        "DELETE FROM user WHERE username = ?", (username_to_delete,)
    )
    db_conn.commit()
    
    return jsonify({"message": f"User '{username_to_delete}' deleted successfully"}), 200


@user_bp.route('/list', methods=['GET'])
def list_users():
    print("Listing users...")  # Debugging print
    db_conn = get_db()
    cursor = db_conn.execute("SELECT username FROM user")
    users = [{"username": row["username"]} for row in cursor.fetchall()]
    return jsonify(users), 200


