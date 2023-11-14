# word.py

from fuzzywuzzy import fuzz, process
# words.py

import sqlite3
import spacy
from translate import Translator

spacy_dict = {}
class Words:
    def __init__(self, db_path):
        self.db_path = db_path
        spacy_corpus = {
            'de': 'de_core_news_sm',
            'pl': 'pl_core_news_sm',
            'es': 'es_core_news_sm',
            'en': 'en_core_web_sm',
            'ru': 'ru_core_news_sm',
        }

    def translate_word(self, lemmatized_word, source_language='en', target_language='es'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Check if lemmatized word exists in the database
            cursor.execute('SELECT translation_text FROM words WHERE lemmatized_word = ? AND language_id = (SELECT id FROM language WHERE language_name = ?)', (lemmatized_word, source_language))
            db_translation = cursor.fetchone()

            if db_translation:
                return db_translation[0]
            else:
                # Use translation library to translate the word
                translator = Translator(to_lang=target_language)
                translation = translator.translate(lemmatized_word)
                return translation



    def create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS language (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    language_name TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS definition (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    definition_text TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS translation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    translation_text TEXT NOT NULL
                )
            ''')

    def store_word(self, lemmatized_word, language, definition, translation):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO language (language_name) VALUES (?)', (language,))
            cursor.execute('INSERT INTO definition (definition_text) VALUES (?)', (definition,))
            cursor.execute('INSERT INTO translation (translation_text) VALUES (?)', (translation,))
            language_id = cursor.lastrowid
            definition_id = cursor.lastrowid
            translation_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO words (lemmatized_word, language_id, definition_id, translation_id)
                VALUES (?, ?, ?, ?)
            ''', (lemmatized_word, language_id, definition_id, translation_id))

    def get_word_by_id(self, word_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT words.id, lemmatized_word, language_name, definition_text, translation_text
                FROM words
                JOIN language ON words.language_id = language.id
                JOIN definition ON words.definition_id = definition.id
                JOIN translation ON words.translation_id = translation.id
                WHERE words.id = ?
            ''', (word_id,))
            return cursor.fetchone()

    def get_all_words(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT words.id, lemmatized_word, language_name, definition_text, translation_text
                FROM words
                JOIN language ON words.language_id = language.id
                JOIN definition ON words.definition_id = definition.id
                JOIN translation ON words.translation_id = translation.id
            ''')
            return cursor.fetchall()
