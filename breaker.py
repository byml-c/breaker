import json
import time
import logging

from log import logger
from database_sqlite import database

# from ndwy_rss import ndwy_rss
from ndwy_login import ndwy_login
from website import website

from search import search
from send_email import server

class breaker:
    users = []

    def __init__(self):
        '''
            初始化，并读取用户数据库，日志
        '''
        self.announces = [
            {'name': '校团委', 'en': 'tuanwei', 'url': 'https://tuanwei.nju.edu.cn'},
            {'name': '本科生院', 'en': 'bksy', 'url': 'https://jw.nju.edu.cn'}
        ]

        self.db = database('users')
        self.read_user_data()

        self.log = logger('breaker')
    
    def log(self, content:str, type:str='D'):
        '''
            写入日志

            type: 消息类型
                D: debug, I: info, W: warning, E: error
            content: 写入内容
        '''
        
        if type == 'D':
            logging.debug(content)
        elif type == 'I':
            logging.info(content)
        elif type == 'W':
            logging.warning(content)
        elif type == 'E':
            logging.error(content)

    def read_user_data(self)->None:
        '''
            读取用户数据
        '''

        self.users = []
        user_data = self.db.findall()
        for user in user_data:
            user = list(user)
            if user[1] == 'utime': continue
            else: self.users.append(json.loads(user[0]))

    def update(self)->None:
        '''
            运行爬虫，进行筛选，发送邮件
        '''

        try:
            # 读取用户数据
            self.read_user_data()

            # 运行爬虫，进行更新
            for item in self.announces:
                website(item['name'], item['en'], item['url']).update()
                self.log.write(f'''通知网站：{item['name']} 更新完成！''', 'I')
                # 对象不再被引用时，会自动析构
            # ndwy_rss().update()
            ndwy_login(1).update()
            self.log.write(f'五育系统更新成功！', 'I')

            # 创建搜索和邮件发送对象
            search_obj = search()
            server_obj = server()

            # 读取并更新时间戳
            timestamp = self.db.last_update_time()
            self.db.set_update_time(time.time())

            # 群发通知信息
            announce = search_obj.search_website(timestamp)
            for item in announce:
                server_obj.send_item(item, self.users)
            
            # 个性化推送五育消息
            for user in self.users:
                wy = search_obj.search_ndwy(user)
                if len(wy) > 0:
                    server_obj.send_ndwy_list(user, wy)
            
            self.log.write('更新完成！', 'I')
        
        except Exception as err:
            self.log.write(f'更新出错！错误: {err}.', 'E')
    
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
    # print(a.users)
    a.db.set_update_time(time.mktime(
                     time.strptime('2023-11-17 Friday 00:00:00', '%Y-%m-%d %A %H:%M:%S')))
    a.modify_user_data({
        'name': 'QwQ',
        'tspan': [0, 0],
        'wbtime': [[0, 36600, 40200], [0, 40200, 50400], [0, 50400, 54000], [0, 54000, 58200], [0, 58200, 61800], [0, 61800, 66600], [1, 36600, 40200], [1, 40200, 50400], [1, 66600, 70200], [1, 70200, 73800], [2, 32400, 36600], [2, 36600, 40200], [2, 54000, 58200], [2, 58200, 61800], [3, 66600, 70200], [3, 28800, 32400], [3, 32400, 36600], [3, 36600, 40200], [3, 58200, 61800], [3, 61800, 66600], [3, 66600, 70200], [3, 66600, 70200], [4, 54000, 58200], [4, 58200, 61800], [4, 61800, 66600]],
        'dbtime': [],
        'kwords': [],
        'type': [],
        'valid': True,
        'address': '231880291@smail.nju.edu.cn',
        'academy': '4907',
        'grade': '2023',
        'degree': '0'
    })

    # 同学一
    # a.modify_user_data({
    #     'name': '',
    #     'tspan': [0, 0],
    #     'wbtime': [],
    #     'dbtime': [],
    #     'kwords': [],
    #     'type': [],
    #     'valid': True,
    #     'address': '@smail.nju.edu.cn',
    #     'academy': '',
    #     'grade': '2023',
    #     'degree': '0'
    # })

    # 同学二
    # a.modify_user_data({
    #     'name': '',
    #     'tspan': [0, 0],
    #     'wbtime': [],
    #     'dbtime': [],
    #     'kwords': [],
    #     'type': [],
    #     'valid': True,
    #     'address': '@smail.nju.edu.cn',
    #     'academy': '',
    #     'grade': '2023',
    #     'degree': '0'
    # })
    a.update()