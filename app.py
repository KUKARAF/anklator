from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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





@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    wdb = word_db(app)
    # Your index view logic here
    return render_template('index.html', languages=wdb.get_all_languages())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        udb = user_db(app)
        username = request.form['username']
        password = request.form['password']
        if udb.login_user(user, username, password)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        udb = user_db(app)
        if create_user(username, password):
            return redirect(url_for('login'))

    return render_template('register.html')

@login_required
@app.route('/add_language_form')
def add_language_form():
    wdb = word_db(app)
    return render_template('add_language_form.html', available_languages=wdb.get_all_languages())


@login_required
@app.route('/add-language', methods=[ 'POST'])
def add_language():
    lang = request.form.get("language")
    wdb = word_db(app)
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
        words = Words(db_path=current_user.words_db_path)  # Pass the user's words database path
        translated_word = words.translate_word(word, sourceLanguage, targetLanguage)
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
    create_tables()  # Add this line to create tables
    app.run(debug=True)

