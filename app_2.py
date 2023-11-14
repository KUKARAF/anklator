from flask import Flask, render_template, request, g, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from word import Words  # Import the Words class from the word module

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['DATABASE'] = 'word_db.sqlite'  # Specify the word database path
app.config['USERS_DATABASE'] = 'passwords.sqlite'  # Specify the user database path

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    def __getattr__(self, item):
        if item == 'words_db_path':
            return f"user_db/{self.username}/words.sqlite"


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    if user_data:
        return User(user_data[0], user_data[1])
    return None

def get_user_by_id(user_id):
    with app.app_context():
        db = get_users_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
        return cursor.fetchone()

def get_user_by_username(username):
    with app.app_context():
        db = get_users_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        return cursor.fetchone()

def create_tables():
    with app.app_context():
        db = get_users_db()
        cursor = db.cursor()
        # Create the users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        ''')
        db.commit()
def create_user_tables(user_words_db_path):
    # Create the necessary tables for a new user

    with sqlite3.connect(user_words_db_path) as user_db:
        cursor = user_db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lemmatized_word TEXT NOT NULL,
                translation_text TEXT NOT NULL,
                language_id INTEGER NOT NULL,
                FOREIGN KEY (language_id) REFERENCES language (id)
            )
        ''')
        # Create the language table if it doesn't exist

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS language (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language_name TEXT NOT NULL UNIQUE
            )
        ''')
        user_db.commit()


def create_user(username, password):
    with app.app_context():
        db = get_users_db()
        cursor = db.cursor()

        if get_user_by_username(username):
            flash('Username already exists. Please choose a different one.', 'error')
            return False

        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                       (username, password_hash))
        db.commit()
        user_db_folder = os.path.dirname(current_user.words_db_path)
        os.makedirs(user_db_folder, exist_ok=True)  # Create the user database folder if it doesn't exist
        create_user_tables(current_user.words_db_path)
        flash('Account created successfully!', 'success')
        return True

def verify_user(username, password):
    with app.app_context():
        db = get_users_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            return User(user[0], user[1])

        flash('Invalid username or password. Please try again.', 'error')
        return None

def get_users_db():
    db = getattr(g, '_users_database', None)
    if db is None:
        db = g._users_database = sqlite3.connect(app.config['USERS_DATABASE'])
    return db


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Your index view logic here
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
@login_required
def translate():
    if request.method == 'POST':
        word = request.form['word']
        words = Words(db_path=current_user.words_db_path)  # Pass the user's words database path
        translated_word = words.translate_word(word)
        return translated_word

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = verify_user(username, password)

        if user:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if create_user(username, password):
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/protected')
@login_required
def protected():
    return f'Hello, {current_user.id}! This is a protected route.'

@app.route('/languages')
def get_languages():
    languages = [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        # Add more languages as needed
    ]
    return jsonify({"languages": languages})

# ... (the rest of your code remains unchanged)

if __name__ == '__main__':
    create_tables()  # Add this line to create tables
    app.run(debug=True)

