import sqlite3
import json
from sqlite3 import OperationalError 
from user_db_manager import user_db
from flask_login import UserMixin
from translate import Translator
from spacy.cli.download import download

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    def __getattr__(self, item):
        if item == 'words_db_path':
            return f"user_db/{self.username}/words.sqlite"
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

class word_db:

    def __init__(self, app):
        self.user_db = user_db(app)


    def create_word_tables(self):
        with sqlite3.connect(self.user_db.get_word_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lemmatized_word TEXT NOT NULL,
                    language_id INTEGER,
                    definition_id INTEGER,
                    translation_id INTEGER,
                    FOREIGN KEY (language_id) REFERENCES language(id),
                    FOREIGN KEY (definition_id) REFERENCES definition(id),
                    FOREIGN KEY (translation_id) REFERENCES translation(id)
                )
            ''')
            conn.commit()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS word_relationships (
                    word_id1 INTEGER,
                    word_id2 INTEGER,
                    FOREIGN KEY (word_id1) REFERENCES words(id),
                    FOREIGN KEY (word_id2) REFERENCES words(id)
                )
            ''')
            conn.commit()
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS languages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        language TEXT NOT NULL, 
                        language_code TEXT,
                        spacy_corpus TEXT
                    )
                ''')
            conn.commit()
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS definitions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        definition_text TEXT NOT NULL
                    )
                ''')
            conn.commit()



    def add_translation(self, lemmatized_word, source_language='en', target_language='es'):
        with sqlite3.connect(self.user_db.get_word_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM words WHERE lemmatized_word = ? AND language_id = (SELECT id FROM languages WHERE language_name = ?)', (lemmatized_word, source_language))
            word_id = cursor.fetchone()[0]
            translator = Translator(to_lang=target_language)
            translation = translator.translate(lemmatized_word)
            cursor.execute('INSERT INTO words (lemmatized_word, language_id) VALUES (?, (SELECT id FROM languages WHERE language_name = ?))', (translation, target_language))
            translation_id = cursor.lastrowid
            cursor.execute('INSERT INTO word_relationships (word_id1, word_id2) VALUES (?, ?)', (word_id, translation_id))
            conn.commit()
            return translation_id

    def search_translation(self, lemmatized_word, source_language='en', target_language='es'):
        with sqlite3.connect(self.user_db.get_word_db_path()) as conn:
            cursor = conn.cursor()
            # Query to find if the translation already exists
            cursor.execute('''
                SELECT translation_text FROM words 
                JOIN language ON words.language_id = language.id
                WHERE lemmatized_word = ? AND language_name = ?
            ''', (lemmatized_word, target_language))
            result = cursor.fetchone()
            return result[0] if result else False

    def add_translation(self, lemmatized_word, source_language='en', target_language='es'):
        # First, check if the translation already exists to avoid duplicates
        existing_translation = self.search_translation(lemmatized_word, source_language, target_language)
        if existing_translation:
            return existing_translation
        else:
            with sqlite3.connect(self.user_db.get_word_db_path()) as conn:
                cursor = conn.cursor()
                # Translate the word using the Translator
                translator = Translator(to_lang=target_language)
                translation = translator.translate(lemmatized_word)
                # Insert the new translation into the database
                cursor.execute('''
                    INSERT INTO words (lemmatized_word, language_id) 
                    VALUES (?, (SELECT id FROM languages WHERE language_name = ?))
                ''', (translation, target_language))
                translation_id = cursor.lastrowid
                # Find the word_id for the source language word
                cursor.execute('''
                    SELECT id FROM words 
                    WHERE lemmatized_word = ? AND language_id = (SELECT id FROM languages WHERE language_name = ?)
                ''', (lemmatized_word, source_language))
                word_id = cursor.fetchone()[0]
                # Insert the relationship between the words
                cursor.execute('''
                    INSERT INTO word_relationships (word_id1, word_id2) 
                    VALUES (?, ?)
                ''', (word_id, translation_id))
                conn.commit()
                return translation_id

    def add_word(self, lemmatized_word, language, definition, translation=None):
        with sqlite3.connect(self.user_db.get_word_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO language (language_code, language_name, spacy_corpus) VALUES (?, ?, ?)', (language_code, language_name, spacy_corpus,))
            cursor.execute('INSERT INTO definition (definition_text) VALUES (?)', (definition,))
            language_id = cursor.lastrowid
            definition_id = cursor.lastrowid
            cursor.execute('INSERT INTO words (lemmatized_word, language_id, definition_id) VALUES (?, ?, ?)', (lemmatized_word, language_id, definition_id))
            word_id = cursor.lastrowid
            if translation:
                translation_id = self.translate(lemmatized_word, language, translation)
                cursor.execute('INSERT INTO word_relationships (word_id1, word_id2) VALUES (?, ?)', (word_id, translation_id))
            conn.commit()

    def add_lang(self, lang):
        with sqlite3.connect(self.user_db.get_word_db_path()) as conn:
            cursor = conn.cursor()
            with open('lang_codes/language-codes.json', 'r') as file:
                languages = json.load(file)
                lang = next((item for item in languages if item["Language Code"] == lang), None)
                cursor.execute('SELECT id FROM languages WHERE language = ?', (lang['Language'],))
                if cursor.fetchone() is None:
                        cursor.execute('''
                            INSERT INTO languages (language, language_code, spacy_corpus)
                            VALUES (?, ?, ?)
                        ''', (lang['Language'], lang['Language Code'], lang['Corpus Name']))
                        download(lang['Corpus Name'])
                        conn.commit()
                        return True
                else: 
                    return False

    def get_all_languages(self):
        with sqlite3.connect(self.user_db.get_word_db_path()) as conn:
            cursor = conn.cursor()
            try: 
                cursor.execute('SELECT language FROM languages')
                return [language[0] for language in cursor.fetchall()]
            except OperationalError:
                return False
