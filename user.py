import json
import time
from log import logger
from database_sqlite import database

class users:
    users = []
    def __init__(self):
        '''
            初始化，读取用户数据库
        '''

        self.db = database('users')
        self.read()
    
    def read(self):
        '''
            读取用户数据
        '''

        self.users = []
        user_data = self.db.findall()
        for user in user_data:
            user = list(user)
            if user[1] == 'utime': continue
            else: self.users.append(json.loads(user[0]))

    def modify(self, user:dict)->None:
        '''
            修改用户数据，不存在则新建对应用户

            user: 用户数据
        '''

        if not self.db.exist(user['name']):
            self.users.append(user)
        else:
            for i in range(0, len(self.users)):
                if self.users[i]['name'] == user['name']:
                    self.users[i] = user
                    break
            self.db.remove(user['name'])
        
        self.db.insert(user['name'], json.dumps(user), int(time.time()))
