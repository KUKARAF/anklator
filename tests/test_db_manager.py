import pytest 
import sys
sys.path.insert(0, '/home/rafa/dev/vocab_translator')
from word import Words


@pytest.fixture
def words():
    return Words('test_db.sqlite')

def test_translate(words):
    translation_id = words.translate('hello', 'en', 'es')
    assert translation_id is not None

    with sqlite3.connect(words.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM word_relationships WHERE word_id1 = ? AND word_id2 = ?', (1, translation_id))
        assert cursor.fetchone() is not None

def test_add_word(words):
    words.add_word('hello', 'en', 'Hello, World!', 'es')
    with sqlite3.connect(words.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM words WHERE lemmatized_word = ?', ('hello',))
        assert cursor.fetchone() is not None

        cursor.execute('SELECT * FROM word_relationships WHERE word_id1 = ? AND word_id2 = ?', (1, 2))
        assert cursor.fetchone() is not None

def test_translate_nonexistent_word(words):
    with pytest.raises(Exception):
        words.translate('nonexistentword', 'en', 'es')

def test_multiple_translations(words):
    translation_id1 = words.translate('bank', 'en', 'es')
    translation_id2 = words.translate('bank', 'en', 'es')
    assert translation_id1 != translation_id2


def test_duplicate_entries(words):
    words.add_word('hello', 'en', 'Hello, World!', 'es')
    with pytest.raises(Exception):
        words.add_word('hello', 'en', 'Hello, World!', 'es')

def test_unsupported_languages(words):
    with pytest.raises(Exception):
        words.translate('hello', 'en', 'unsupported_language')

def test_long_words_and_definitions(words):
    long_word = 'a' * 1000
    long_definition = 'a' * 1000
    words.add_word(long_word, 'en', long_definition, 'es')

def test_empty_strings(words):
    with pytest.raises(Exception):
        words.translate('', 'en', 'es')
    with pytest.raises(Exception):
        words.add_word('', 'en', 'Hello, World!', 'es')
