import sqlite3
import hashlib
import time

class database:
    def __init__(self, table_en_name:str,
                 update_time:float=time.mktime(
                     time.strptime('2023-10-01 Sunday 00:00:00', '%Y-%m-%d %A %H:%M:%S'))):
        '''
            初始化数据表

            table_en_name: 数据表的存储名称
            update_name: 初始化数据表中的更新时间戳
        '''

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
        '''
            析构函数，负责删除数据表
        '''

        self.close()

    def close(self)->None:
        self.db_connect.close()
        print(f'Database {self.table_name} has been closed successfully!')

    @staticmethod
    def md5(s:str)->str:
        '''
            使用 MD5 算法对字符串取哈希值
        '''

        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def exist(self, s_id:str)->bool:
        '''
            判断表中是否存在值
            s_id: 带取哈希值的 id 字符串
        '''

        s_id = self.md5(s_id)
        query = f'''SELECT * FROM {self.table_name} WHERE hash='{s_id}';'''

        if len(list(self.db_cursor.execute(query))) > 1:
            return True
        else:
            return False

    def insert(self, s_id:str, data:str, rtime:float)->None:
        '''
            向表中加入新数据

            s_id: 带取哈希值的 id 字符串
            data: json 转义后的数据字符串
            rtime: 列表项的时间戳
        '''

        s_id = self.md5(s_id)
        query = f'''INSERT INTO {self.table_name} (content, hash, rtime) VALUES ('{data}', '{s_id}', '{rtime}');'''
        self.db_cursor.execute(query)
        self.db_connect.commit()

    def remove(self, s_id:str)->None:
        '''
            删除表中 s_id 对应的数据

            s_id: 带取哈希值的 id 字符串
        '''

        s_id = self.md5(s_id)
        query = f'''DELETE FROM {self.table_name} WHERE hash='{s_id}';'''
        self.db_cursor.execute(query)
        self.db_connect.commit()

    def last_update_time(self)->float:
        '''
            读取存储在表第一列的更新时间戳
        '''

        query = f'''SELECT "content" FROM {self.table_name} WHERE hash="utime";'''
        self.db_cursor.execute(query)
        return float(self.db_cursor.fetchone()[0])

    def set_update_time(self, timestamp:float)->None:
        '''
            设置存储在表第一列的更新时间戳

            timestamp: 将时间戳设置为的值
        '''

        query = f'''UPDATE {self.table_name} SET "content"={str(timestamp)} WHERE hash="utime";'''
        self.db_cursor.execute(query)
        self.db_connect.commit()

    def findall(self)->list:
        '''
            返回所有表中的所有数据
        '''

        query = f'''SELECT * FROM {self.table_name};'''
        self.db_cursor.execute(query)
        return self.db_cursor.fetchall()

    def search_by_timestamp(self, timestamp:float)->list:
        '''
            返回所有表中时间戳在给定时间戳之后的所有数据

            timestamp: 给定时间戳
        '''

        query = f'''SELECT "content", "rtime" FROM {self.table_name} WHERE rtime >= {timestamp}'''
        self.db_cursor.execute(query)
        return self.db_cursor.fetchall()