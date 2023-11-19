import json
import time

from database_sqlite import database

# from ndwy_rss import ndwy_rss
from ndwy_login import ndwy_login
from website import website

from search import search
from send_email import server

class breaker:
    
    def __init__(self):
        '''
            初始化，并读取用户数据库
        '''
        self.announces = [
            {'name': '校团委', 'en': 'tuanwei', 'url': 'https://tuanwei.nju.edu.cn'},
            {'name': '本科生院', 'en': 'bksy', 'url': 'https://jw.nju.edu.cn'}
        ]

        self.db = database('users')
        user_data = self.db.findall()
        self.users = []
        for user in user_data:
            user = list(user)
            if user[1] == 'utime':
                continue
            else: self.users.append(json.loads(user[0]))
    
    def update(self)->None:
        '''
            运行爬虫，进行筛选，发送邮件
        '''

        # 运行爬虫，进行更新
        for item in self.announces:
            website(item['name'], item['en'], item['url']).update()
            print(f'''通知网站：{item['name']} 更新完成！''')
            # 对象不再被引用时，会自动析构
        # ndwy_rss().update()
        ndwy_login().update()
        print(f'五育系统更新成功！')

        # 创建搜索和邮件发送对象
        search_obj = search()
        server_obj = server()
        timestamp = self.db.last_update_time()

        # 群发通知信息
        announce = search_obj.search_website(timestamp)
        for item in announce:
            server_obj.send_item(item, self.users)
        
        # 个性化推送五育消息
        for user in self.users:
            wy = search_obj.search_ndwy(user)
            if len(wy) > 0:
                server_obj.send_ndwy_list(user, wy)
        
        print(f'''Update finish on {
            time.strftime(r'%Y.%m.%d %H:%M:%S', time.localtime())}.''')
    
    def modify_user_data(self, user:dict)->None:
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

if __name__ == '__main__':
    a = breaker()
    a.update()
    # print(a.users)
    a.db.remove('QwQ')
    a.modify_user_data({
        'name': 'QwQ',
        'tspan': [0, 0],
        'wbtime': [],
        'dbtime': [],
        'kwords': [],
        'type': [],
        'valid': True,
        'address': '231880291@smail.nju.edu.cn',
        'academy': '0',
        'grade': '0',
        'degree': '0'
    })