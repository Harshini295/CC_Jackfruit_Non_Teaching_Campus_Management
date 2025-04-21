import os
from flask import Flask
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from app.routes import register_routes


mysql = MySQL()

def create_app():
    load_dotenv()  # Load from .env file

    app = Flask(__name__, static_url_path='/static')
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_key')

    # MySQL Config
    app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'db')  # Docker service name
    app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'Domaaru07,')
    app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'student_welfare')
    app.config['MYSQL_PORT'] = 3306  # Internal container port

    mysql.init_app(app)

    register_routes(app, mysql)

    return app

app = create_app()
# This should be in your main entry script, not in the function
if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0', port=5002)
