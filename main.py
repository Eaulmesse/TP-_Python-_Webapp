import sqlite3
from flask import Flask, render_template, request, g, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

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
            return "L'utilisateur " + username + " existe déjà."
        
        db = get_db()
        query_db("INSERT INTO User (name, password) VALUES (?, ?)", [username , generate_password_hash(password)])
        db.commit()
        
        return redirect(url_for('home'))
        
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST': 
        username = request.form['name']
        password = request.form['password']

        user = query_db("SELECT * FROM User WHERE name = ?", [username], one=True)

        if user:
            stored_password = user['password']
            if check_password_hash(stored_password, password):
                session['user'] = {'id': user['id'], 'name': user['name']}
                return redirect(url_for('dashboard'))
            else: 
                return "Identifiants invalides"
        else:
            return "Utilisateur inexistant"
        
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)  
    return redirect(url_for('home'))

@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))  
    
    expenses = query_db("SELECT * FROM Frais WHERE user_id = ?", [session['user']['id']])
    balance = query_db("SELECT * FROM Solde WHERE user_id = ?", [session['user']['id']])

    return render_template("dashboard.html", expenses=expenses, balance=balance)


@app.route("/dashboard/create/expense", methods=['GET', 'POST'])
def create_expense():
    
    if 'user' not in session:
        return redirect(url_for('login'))  
    
    if request.method == 'POST':
        name = request.form['name']
        value = request.form['value']
        user_id = session['user']['id']
        
        db = get_db()
        query_db("INSERT INTO Frais (name, value, user_id) VALUES (?, ?, ?)", [name , value, user_id])
        db.commit()
        
        return redirect(url_for('dashboard'))

    return render_template("create_expense.html")  
 
@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    if 'user' not in session:
        return redirect(url_for('login')) 

    db = get_db()
    db.execute('DELETE FROM Frais WHERE id = ?', [expense_id])
    db.commit()   

    return redirect(url_for('dashboard'))

@app.route("/dashboard/create/balance", methods=['GET', 'POST'])
def create_balance():  # Python utilise des noms de fonctions en minuscules avec des underscores
    if 'user' not in session:
        return redirect(url_for('login'))  
    
    # Vérifiez d'abord si l'utilisateur a déjà un solde.
    existing_balance = query_db("SELECT * FROM Solde WHERE user_id = ?", [session['user']['id']], one=True)
    if existing_balance:
        # Rediriger l'utilisateur vers le tableau de bord s'il a déjà un solde
        return redirect(url_for('dashboard'))
    
    # Créer un nouveau solde si la méthode est POST et qu'aucun solde n'existe.
    if request.method == 'POST':
        value = request.form['value']
        db = get_db()
        db.execute("INSERT INTO Solde (user_id, value) VALUES (?, ?)", [session['user']['id'], value])
        db.commit()
        return redirect(url_for('dashboard'))

    # Si la méthode n'est pas POST ou si aucun autre cas n'est rencontré, afficher le formulaire de création du solde.
    return render_template("create_balance.html")

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='User'")
        table_exists = cursor.fetchone()
        if not table_exists:
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()

init_db()


