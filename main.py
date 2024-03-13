import sqlite3

from flask import Flask, render_template, current_app, g

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")


DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='User';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()


init_db()