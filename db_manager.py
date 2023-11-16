import sqlite3


class DBmanager:

    def __init__(self, db_path):
        self.db_path = db_path

def create_word_tables(self):
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
            CREATE TABLE IF NOT EXISTS word_relationships (
                word_id1 INTEGER,
                word_id2 INTEGER,
                FOREIGN KEY (word_id1) REFERENCES words(id),
                FOREIGN KEY (word_id2) REFERENCES words(id)
            )
        ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS languages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    language TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    definition_text TEXT NOT NULL
                )
            ''')
            conn.commit()



    def translate(self, lemmatized_word, source_language='en', target_language='es'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM words WHERE lemmatized_word = ? AND language_id = (SELECT id FROM language WHERE language_name = ?)', (lemmatized_word, source_language))
            word_id = cursor.fetchone()[0]
            translator = Translator(to_lang=target_language)
            translation = translator.translate(lemmatized_word)
            cursor.execute('INSERT INTO words (lemmatized_word, language_id) VALUES (?, (SELECT id FROM language WHERE language_name = ?))', (translation, target_language))
            translation_id = cursor.lastrowid
            cursor.execute('INSERT INTO word_relationships (word_id1, word_id2) VALUES (?, ?)', (word_id, translation_id))
            conn.commit()
            return translation_id

    def add_word(self, lemmatized_word, language, definition, translation=None):
        with sqlite3.connect(self.db_path) as conn:
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

    def add_lang(self, lang)
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
