import sqlite3
from contextlib import closing

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('usage.db', check_same_thread=False)
        self._init_db()
    
    def _init_db(self):
        with closing(self.conn.cursor()) as c:
            c.execute('''CREATE TABLE IF NOT EXISTS users 
                       (user_id INT PRIMARY KEY, downloads INT)''')
            self.conn.commit()
    
    def log_download(self, user_id: int):
        with closing(self.conn.cursor()) as c:
            c.execute('''INSERT OR REPLACE INTO users VALUES 
                       (?, COALESCE((SELECT downloads FROM users WHERE user_id=?) + 1, 1))''',
                       (user_id, user_id))
            self.conn.commit()
    
    def get_stats(self):
        with closing(self.conn.cursor()) as c:
            c.execute('''SELECT COUNT(*), SUM(downloads) FROM users''')
            return c.fetchone()
