from app import create_app, db

app = create_app()

if __name__ == '__main__':
    app.run("0.0.0.0", 8000, debug=True)
