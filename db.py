import sqlite3
from datetime import datetime


class DB:
    def __init__(self):
        conn = sqlite3.connect("news.db", check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()

db = DB()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='users'")
        row = cursor.fetchone()
        if row is None:
            self.init_table()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128),
                             admin INTEGER
                             )''')
        cursor.execute('''INSERT INTO users (user_name, password_hash, admin)
                          VALUES (?,?,?)''', ('admin', 'admin', 1))
        cursor.execute('''INSERT INTO users (user_name, password_hash, admin)
                          VALUES (?,?,?)''', ('angel', 'angel', 0))
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users
                          (user_name, password_hash, admin)
                          VALUES (?,?,?)''', (user_name, password_hash, 0))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_by_name(self, user_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?", (user_name,))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)


class NewsModel:
    def __init__(self, connection):
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='news'")
        row = cursor.fetchone()
        if row is None:
            self.init_table()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             title VARCHAR(100),
                             content VARCHAR(1000),
                             user_id INTEGER,
                             pub_date INTEGER,
                             pic VARCHAR(100)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id, pic, edit=None):
        pub_date = round(datetime.timestamp(datetime.now()))
        if edit:
            news = NewsModel(db.get_connection())
            if news.get(edit):
                pub_date = news.get(edit)[4]
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news
                          (title, content, user_id, pub_date, pic)
                          VALUES (?,?,?,?,?)''', (title, content, str(user_id), pub_date, pic))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ?", (str(news_id),))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None, sort=0):
        if sort == 0:
            order = ' ORDER BY pub_date DESC'
        elif sort == 1:
            order = ' ORDER BY title'
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM news WHERE user_id = ?" + order,
                           (str(user_id),))
        else:
            cursor.execute("SELECT * FROM news" + order)
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM news WHERE id = ?''', (str(news_id),))
        cursor.close()
        self.connection.commit()
