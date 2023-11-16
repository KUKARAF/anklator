from flask import g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


class user_db:
    def __init__(self, app):
        
        self.login_manager = LoginManager(app)
        self.login_manager.login_view = 'login'
    def get_users_db():
        db = getattr(g, '_users_database', None)
        if db is None:
            db = g._users_database = sqlite3.connect(app.config['USERS_DATABASE'])
        return db

    def create_user_tables(self):
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
    def word_db_path(self):
        return current_user.words_db_path)

    def create_user(self, username, password):
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
            flash('Account created successfully!', 'success')
            return True

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

    def get_user_by_id(self, user_id):
        with app.app_context():
            db = self.get_users_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
            return cursor.fetchone()

    def get_user_by_username(self, username):
        with app.app_context():
            db = self.get_users_db()
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE username=?', (username,))
            return cursor.fetchone()

    @login_manager.user_loader
    def load_user(self, user_id):
        user_data = self.get_user_by_id(user_id)
        if user_data:
            return User(user_data[0], user_data[1])
        return None
    
    def login_user(self, username, password)
        user = self.verify_user(username, password)
        if user:
            login_user(user)
            user_db_folder = os.path.dirname(current_user.words_db_path)
            os.makedirs(user_db_folder, exist_ok=True)  # Create the user database folder if it doesn't exist
            db = user_db(current_user.words_db_path)
            db.create_word_tables()
            flash('Login successful!', 'success')


class User(self, UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    def __getattr__(self, item):
        if item == 'words_db_path':
            return f"user_db/{self.username}/words.sqlite"
