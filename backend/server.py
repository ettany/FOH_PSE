from app import create_app  # Make sure this is correct

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Set the port as needed
