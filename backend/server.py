from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(port=5000)  # Run the backend on port 5000
