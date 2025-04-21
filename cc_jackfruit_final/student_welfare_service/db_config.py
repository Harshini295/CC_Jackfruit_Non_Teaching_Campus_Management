from flask_mysqldb import MySQL

def init_db(app):
    mysql = MySQL(app)
    return mysql
