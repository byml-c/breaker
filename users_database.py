import sqlite3
import json
import time
import hashlib

class user_database:
    def __init__(self,
                 update_time:float=time.mktime(
                     time.strptime('2023-11-25 Saturday 00:00:00', '%Y-%m-%d %A %H:%M:%S'))):
        """
        初始化数据表

        table_en_name: 数据表的名称
        update_name: 初始化数据表中的更新时间戳
        """

        self.table_name = 'users'
        self.db_connect = sqlite3.connect("nova.db")
        self.db_cursor = self.db_connect.cursor()

        query = f'''SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}';'''
        self.db_cursor.execute(query)
        if self.db_cursor.fetchone() is None:
            self.create_table(update_time)

        print(f"Database users has been opened successfully!")

    def close(self) -> None:
        self.db_connect.close()
        print(f"Database {self.table_name} has been closed successfully!")

    @staticmethod
    def md5(s: str) -> str:
        return hashlib.md5(s.encode("utf-8")).hexdigest()

    def exist(self, email: str) -> bool:
        """
        判断表中是否存在值
        s_id: 带取哈希值的 id 字符串
        """
        h_email = self.md5(email)
        query = f"""SELECT * FROM {self.table_name} WHERE hash='{h_email}';"""

        if len(list(self.db_cursor.execute(query))) > 0:
            return True
        else:
            return False

    def remove_database(self):
        self.db_cursor.execute(f'DROP TABLE {self.table_name};')

    def insert(
        self,
        name: str,
        email: str,
        busytime: list[str],
        grade: int,
        academy: str,
        degree: str,
    ) -> None:
        """
        向表中加入新数据
        busytime: 列表项的时间戳
        """

        h_email = self.md5(email)
        j_busytime = json.dumps(busytime)
        print("The data have been converted!")
        query = f"""
        INSERT INTO {self.table_name} (name, hash, email, busytime, grade, academy, degree) VALUES ('{name}', '{h_email}', '{email}', '{j_busytime}', '{grade}', '{academy}','{degree}');
        """
        self.db_cursor.executescript(query)
        self.db_connect.commit()

    def remove(self, email: str) -> None:
        """
        删除表中 email 对应的数据

        h_email: 取哈希值的email字符串
        """

        h_email = self.md5(email)
        query = f"""DELETE FROM {self.table_name} WHERE hash='{h_email}';"""
        self.db_cursor.execute(query)
        self.db_connect.commit()

    def search(self, email: str) -> dict:
        h_email = self.md5(email)
        query = f"""
                SELECT * FROM {self.table_name} WHERE hash = '{h_email}';
        """
        self.db_connect.row_factory = sqlite3.Row
        self.db_cursor.execute(query)
        row = self.db_cursor.fetchone()
        return dict(row)

    def create_table(self, update_time):
        query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name}
            (
                name        TEXT    NOT NULL,
                hash        TEXT    PRIMARY KEY,
                email       TEXT    NOT NULL,
                busytime    JSON,
                grade       INT,
                academy     TEXT,
                degree      TEXT
            );
        """
        self.db_cursor.execute(query)
        # 加入时间戳
        query = f'''INSERT INTO {self.table_name} (name, hash, email) VALUES ('{str(update_time)}', 'utime', '');'''
        self.db_cursor.execute(query)
        self.db_connect.commit()
        print("The table has been added successfully!")

    def fetch_all(self) -> list:
        query = f"""SELECT * FROM {self.table_name}"""
        self.db_cursor.execute(query)
        return self.db_cursor.fetchall()

    def last_update_time(self)->float:
        '''
            读取存储在表第一列的更新时间戳
        '''

        query = f'''SELECT "name" FROM {self.table_name} WHERE hash="utime";'''
        self.db_cursor.execute(query)
        return float(self.db_cursor.fetchone()[0])

    def set_update_time(self, timestamp:float)->None:
        '''
            设置存储在表第一列的更新时间戳

            timestamp: 将时间戳设置为的值
        '''

        query = f'''UPDATE {self.table_name} SET "name"={str(timestamp)} WHERE hash="utime";'''
        self.db_cursor.execute(query)
        self.db_connect.commit()


if __name__ == "__main__":
    db = user_database("users")
    # db.remove_database()
    # dicts = db.fetch_all()
    # db.close()