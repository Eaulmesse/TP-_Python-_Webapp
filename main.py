import sqlite3
from flask import Flask, render_template, request, g, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row 
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']

        if query_db("SELECT name FROM User WHERE name = ?", [username], one=True) is not None:
            return "L'utilisateur " + username + " existe déjà "

        
        db = get_db()
        cursor = db.cursor()
        
        query_db("INSERT INTO User (name, password) VALUES (?, ?)", [username , generate_password_hash(password)])
        db.commit()
        
    
    
        cursor.close()
        return redirect(url_for('home'))
        
    return render_template("register.html")

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


