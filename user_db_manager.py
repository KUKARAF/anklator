from flask_login import login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import g, flash
import sqlite3


class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    def __getattr__(self, item):
        if item == 'words_db_path':
            return f"user_db/{self.username}/words.sqlite"
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

class user_db:
    def __init__(self, app):
        self.app = app 

    def get_users_db(self):
        with self.app.app_context():
            db = getattr(g, '_users_database', None)
            if db is None:
                db = g._users_database = sqlite3.connect(self.app.config['USERS_DATABASE'])
            return db
    def create_user_tables(self, db):
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
    def get_word_db_path(self):
        return current_user.words_db_path

    def verify_user(self, username, password):
        with app.app_context():
            db = self.get_users_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE username=?', (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[2], password):
                return User(user[0], user[1])

            flash('Invalid username or password. Please try again.', 'error')
            return None

    def login_user(self, username, password): 
        with self.app.app_context():
            user = self.verify_user(username, password)
            if user:
                login_user(user, password)
                flash('Login successful!', 'success')
                return True
            
        
    def create_user(self, username, password):
        with self.app.app_context():
            db = self.get_users_db()
            cursor = db.cursor()

            if self.get_user_by_username(username):
                flash('Username already exists. Please choose a different one.', 'error')
                return False

            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                           (username, password_hash))
            db.commit()
            with self.app.app_context():
                flash('Account created successfully!', 'success')
            return True

    def verify_user(self, username, password):
        with self.app.app_context():
            db = self.get_users_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE username=?', (username,))
            user_s = cursor.fetchone()
            if user_s and check_password_hash(user_s[2], password):
                return User(user_s[0], user_s[1])
            flash('Invalid username or password. Please try again.', 'error')
            return None

    def get_user_by_id(self, user_id):
        with self.app.app_context():
            db = self.get_users_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
            return cursor.fetchone()

    def get_user_by_username(self, username):
        with self.app.app_context():
            db = self.get_users_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE username=?', (username,))
            return cursor.fetchone()
    

