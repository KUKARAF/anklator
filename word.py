# word.py
from spacy.cli.download import download
from fuzzywuzzy import fuzz, process
import json
import sqlite3
import spacy
from translate import Translator

spacy_dict = {}
class Words:
    def __init__(self, db_path):
        self.db_path = db_path
        self.spacy_corpus = {
            'de': 'de_core_news_sm',
            'pl': 'pl_core_news_sm',
            'es': 'es_core_news_sm',
            'en': 'en_core_web_sm',
            'ru': 'ru_core_news_sm',
        }

    def translate_word(self, lemmatized_word, source_language='en', target_language='es'):

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT translation_text FROM words WHERE lemmatized_word = ? AND language_id = (SELECT id FROM language WHERE language_name = ?)', (lemmatized_word, source_language))
            db_translation = cursor.fetchone()
            if db_translation:
                print("returning existing word")
                return db_translation[0]
            else:
                translator = Translator(to_lang=target_language)
                translation = translator.translate(lemmatized_word)
                cursor.execute('INSERT INTO words (lemmatized_word, language_id) VALUES (?, (SELECT id FROM language WHERE language_name = ?), ?)', (lemmatized_word, target_language, translation))
                conn.commit()
                return translation


        def create_tables(self):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS words (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        word TEXT NOT NULL,
                        language_id INTEGER,
                        definition_id INTEGER,
                        translation_id INTEGER,
                        FOREIGN KEY (language_id) REFERENCES language(id),
                        FOREIGN KEY (words) REFERENCES words(id),
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
                conn.commit()

    def get_all_languages(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT language_name FROM language')
            return [language[0] for language in cursor.fetchall()]

    def search_language(self, language_code, language_data):
        for language in language_data:
            if language['Language Code'] == language_code:
                return {
                    'Language': language['Language'],
                    'Language Code': language['Language Code'],
                    'Corpus Name': language['Corpus Name']
                }
        return None



    def add_lang(self, search_term=None):
        # Load language codes and names from the JSON file
        with open('lang_codes/language-codes.json', 'r') as file:
            languages = json.load(file)
            if search_term == None:
                return languages
            lang = self.search_language(search_term, languages)
            if lang == None:
                return False

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                    # Check if the language already exists in the database to avoid duplicates
                cursor.execute('SELECT id FROM language WHERE language_code = ?', (lang['Language Code'],))
                if cursor.fetchone() is None:
                    if  search_term == lang['Language Code']:
                        cursor.execute('''
                            INSERT INTO language (language_name, language_code, spacy_corpus)
                            VALUES (?, ?, ?)
                        ''', (lang['Language'], lang['Language Code'], lang['Corpus Name']))
                        download(lang['Corpus Name'])
                        conn.commit()
                        return True
                    else: 
                        return False

    def store_word(self, lemmatized_word, language, definition, translation):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO language (language_code, language_name, spacy_corpus) VALUES (?, ?, ?)', (language_code, language_name, spacy_corpus,))
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
