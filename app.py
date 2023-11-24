from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
from word import Words
from datetime import timedelta
from dotenv import load_dotenv
from word_db_manager import word_db
from user_db_manager import user_db

load_dotenv()
app = Flask(__name__)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(weeks=2)
app.config['SECRET_KEY'] = os.getenv('SECRET')
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
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    if user_data:
        return User(user_data[0], user_data[1])
    return None

def get_users_db():
    db = getattr(g, '_users_database', None)
    if db is None:
        db = g._users_database = sqlite3.connect(app.config['USERS_DATABASE'])
    return db

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


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    wdb = word_db(app)
    langs = wdb.get_all_languages()
    print(langs)
    if langs:
        return render_template('index.html', languages=wdb.get_all_languages())
    else:
        return render_template('index.html', languages=[""])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        udb = user_db(app)
        username = request.form['username']
        password = request.form['password']
        if udb.login_user(username, password):
            wdb = word_db(app)
            wdb.create_word_tables()
            flash('Login successful!', 'success')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        udb = user_db(app)
        if udb.create_user(username, password):
            return redirect(url_for('login'))

    return render_template('register.html')




@login_required
@app.route('/add_language_form')
def add_language_form():
    with open('lang_codes/language-codes.json', 'r') as file:
        languages = json.load(file)
        return render_template('add_language_form.html', available_languages=languages)



@app.route('/create_db')
def create_db():
    wdb = word_db(app)
    wdb.create_word_tables()
    return 'Word database created successfully!'


@login_required
@app.route('/add-language', methods=[ 'POST'])
def add_language():
    lang = request.form.get("language")
    wdb = word_db(app)
    print(lang)
    if wdb.add_lang(lang):
        flash('Login successful!', 'success')
        return 'OK', 200
    else:
        return jsonify({"success": False, "message": "Language not found or not added."}), 404




@login_required
@app.route('/translate', methods=['POST'])
def translate():
    if request.method == 'POST':
        word = request.form['word']
        sourceLanguage = request.form['sourceLanguage']
        targetLanguage = request.form['targetLanguage']
        wdb = word_db(app)
        #words = Words(db_path=current_user.words_db_path)  # Pass the user's words database path
        translated_word = wdb.add_translation(word, sourceLanguage, targetLanguage)
        if not translated_word:
            translated_word = "It doesn't look like anything to me"
        return translated_word


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_required
@app.route('/protected')
def protected():
    return f'Hello, {current_user.id}! This is a protected route.'

@app.route('/languages')
def get_languages():
    current_user.words_db_path
    words_instance = Words(current_user.words_db_path)
    languages = words_instance.get_all_languages()  # Assuming this method exists in Words class
    return jsonify({"languages": languages})



if __name__ == '__main__':
    udb = user_db(app)
    udb.create_user_tables(udb.get_users_db())  # Add this line to create tables
    app.run(debug=True)

