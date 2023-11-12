import sqlite3
import hashlib
import time

class database:
    def __init__(self, table_en_name,
                 update_time=time.mktime(
                     time.strptime('2023-10-01 Sunday 00:00:00', '%Y-%m-%d %A %H:%M:%S'))):
        self.time_format = r'%Y-%m-%d %A %H:%M:%S'
        self.db_connect = sqlite3.connect('nova.db')
        self.db_cursor = self.db_connect.cursor()
        self.table_name = table_en_name

        # 判断传入的表是否存在，如果不存在则新建
        query = f'''SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';'''
        self.db_cursor.execute(query)
        if self.db_cursor.fetchone() is None:
            # 新建表
            self.db_cursor.execute(f'''CREATE TABLE {self.table_name}
            (
                content     TEXT        NOT NULL,
                hash        TEXT        NOT NULL,
                rtime       REAL        NULL
            );
            ''')
            # 加入时间戳
            query = f'''INSERT INTO {self.table_name} (content, hash) VALUES ('{str(update_time)}', 'utime');'''
            self.db_cursor.execute(query)
            self.db_connect.commit()

        print(f'Database {table_en_name} has been opened successfully!')

    def __del__(self):
        self.close()

    def close(self):
        self.db_connect.close()
        print(f'Database {self.table_name} has been closed successfully!')

    @staticmethod
    # md5 转化字符串
    def md5(s):
        assert isinstance(s, str)
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def exist(self, s_id):
        s_id = self.md5(s_id)
        query = f'''SELECT * FROM {self.table_name} WHERE hash='{s_id}';'''

        if len(list(self.db_cursor.execute(query))) > 1:
            return True
        else:
            return False

    def insert(self, s_id, data, rtime):
        s_id = self.md5(s_id)
        query = f'''INSERT INTO {self.table_name} (content, hash, rtime) VALUES ('{data}', '{s_id}', '{rtime}');'''
        self.db_cursor.execute(query)
        self.db_connect.commit()

    def remove(self, s_id):
        s_id = self.md5(s_id)
        query = f'''DELETE FROM {self.table_name} WHERE hash='{s_id}';'''
        self.db_cursor.execute(query)
        self.db_connect.commit()

    def last_update_time(self):
        query = f'''SELECT "content" FROM {self.table_name} WHERE hash="utime";'''
        self.db_cursor.execute(query)
        return float(self.db_cursor.fetchone()[0])

    def set_update_time(self, timestamp):
        query = f'''UPDATE {self.table_name} SET "content"={str(timestamp)} WHERE hash="utime";'''
        self.db_cursor.execute(query)
        self.db_connect.commit()

    def findall(self):
        query = f'''SELECT * FROM {self.table_name};'''
        self.db_cursor.execute(query)
        return self.db_cursor.fetchall()

    def search_by_timestamp(self, timestamp):
        query = f'''SELECT "content", "rtime" FROM {self.table_name} WHERE rtime >= {timestamp}'''
        self.db_cursor.execute(query)
        return self.db_cursor.fetchall()