from app import create_app
from flask_cors import CORS
app = create_app()

CORS(app, support_credentials=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Run the backend on port 5000
