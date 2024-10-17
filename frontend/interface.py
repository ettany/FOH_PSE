from app import create_app  # Import the create_app function from app/__init__.py

app = create_app()  # Initialize the Flask application

if __name__ == "__main__":
    app.run(port=5001)  # Start the Flask app on port 5001
