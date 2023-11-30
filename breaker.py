import json
import time

from log import logger
from database_users import users

from threading import Thread

# from ndwy_rss import ndwy_rss
from ndwy_login import ndwy_login
from website import website
from wechat import wechat

from search import search
from send_email import server

class subthread:
    thread = None
    sub_object = None
    time_accumulation = 0
    def __init__(self, name:str, duration:int, log):
        '''
            初始化计时子线程

            name: 线程名称
            duration: 更新间隔
            log: 日志函数

            create, login, update: 钩子函数
        '''
        self.name = name
        self.active = True
        self.duration = duration

        self.log = log
        self.create = None
        self.login = None
        self.update = None
        self.delete = None
    
    def set_create(self, func):
        self.create = func
    def set_login(self, func):
        self.login = func
    def set_update(self, func):
        self.update = func
    def set_delete(self, func):
        self.delete = func

    def run(self):
        '''
            开启子线程
        '''

        self.thread = Thread(target=self.main)
        self.thread.start()  

    def main(self):
        '''
            子线程主函数
        '''

        self.active = True
        self.log.write(f'子线程 {self.name} 开始运行！', 'I')

        if self.create is not None:
            self.create(self)
        try:
            if self.login is not None:
                res = self.login(self)
                
                if not res:
                    raise Exception('登录失败！')
            
            # 首次运行更新一次
            self.time_accumulation = self.duration
            while self.active:
                if self.time_accumulation >= self.duration:
                    if self.update is not None:
                        self.update(self)
                        if self.active:
                            self.log.write(f'{self.name}完成！', 'I')
                        else:
                            self.log.write(f'{self.name}强制终止！', 'I')
                    self.time_accumulation = 0
                else: self.time_accumulation += 1

                time.sleep(1)
                if self.sub_object:
                    if not self.sub_object.on_alive:
                        self.active = False
        except Exception as err:
            self.active = False
            self.log.write(f'{self.name}出错：{err}', 'E')
        finally:
            if self.delete is not None:
                self.delete(self)
            self.log.write(f'子线程 {self.name} 已停止运行！', 'I')
    
    def restart(self):
        '''
            强制重启子线程
        '''

        self.active = False
        self.log.write(f'子线程 {self.name} 正在等待重启！', 'I')
        # 等待进程停止
        while self.thread.is_alive():
            time.sleep(1)
        self.log.write(f'子线程 {self.name} 正在重启中！', 'I')
        self.run()

    def quit(self):
        '''
            终止子线程
        '''

        self.active = False
    
    def get_status(self, id)->str:
        '''
            以字符串形式返回进程状态

            id: 在主线程中的线程 id 编号
        '''

        if self.active:
            if self.time_accumulation >= self.duration:
                return f'''[{id}] (运行中) 线程名：{self.name}'''
            else:
                return f'''[{id}] (挂起中: 还剩 {self.duration-self.time_accumulation} s) 线程名：{self.name}'''
        else:
            return f'''[{id}] (未运行) 线程名：{self.name}'''

class breaker:
    users = []
    notice_list = [
        {'name': '校团委', 'en': 'tuanwei', 'url': 'https://tuanwei.nju.edu.cn'},
        {'name': '本科生院', 'en': 'bksy', 'url': 'https://jw.nju.edu.cn'}
    ]
    thread_pool = []

    wechat_update_duration = 30*60 # 微信公众号爬虫半小时更新一次
    notice_update_duration = 30*60 # 通知网站爬虫半小时更新一次
    ndwy_update_duration = 60*60 # 五育系统一小时更新一次

    email_timely_duration = 30*60 # 即时发送邮件，半小时一次
    email_ndwy_duration = 30*60 # 五育发送邮件，十二小时一次

    def __init__(self):
        '''
            初始化日志
        '''

        self.users = users()
        self.log = logger('breaker')

    def update_wechat(self)->None:
        '''
            子线程：定时更新微信公众号
        '''
        self.wechat_thread = subthread('微信公众号更新',
                                       self.wechat_update_duration, self.log)
        def create(self):
            self.sub_object = wechat()
        self.wechat_thread.set_create(create)

        def login(self):
            return self.sub_object.auto_login()
        self.wechat_thread.set_login(login)

        def update(self):
            self.sub_object.update()
        self.wechat_thread.set_update(update)

        def delete(self):
            self.sub_object.on_alive = False
            del self.sub_object
        self.wechat_thread.set_delete(delete)

        self.wechat_thread.run()
        self.thread_pool.append(self.wechat_thread)

    def update_notice(self)->None:
        '''
            子线程，定时更新通知网站
        '''

        self.notice_thread = subthread('通知网站更新',
                                       self.notice_update_duration, self.log)
        main_thread = self
        def create(self):
            self.notice_obj_list = [
                website(item['name'], item['en'], item['url'])
                for item in main_thread.notice_list]
        self.notice_thread.set_create(create)

        def update(self):
            for notice in self.notice_obj_list:
                notice.update()
        self.notice_thread.set_update(update)

        def delete(self):
            for notice in self.notice_obj_list:
                del notice
        self.notice_thread.set_delete(delete)

        self.notice_thread.run()
        self.thread_pool.append(self.notice_thread)

    def update_ndwy(self):
        '''
            子线程，定时更新五育网站
        '''

        self.ndwy_thread = subthread('五育系统更新',
                                     self.ndwy_update_duration, self.log)
        def create(self):
            self.sub_object = ndwy_login(1)
        self.ndwy_thread.set_create(create)
        
        def login(self):
            return self.sub_object.auto_login()
        self.ndwy_thread.set_login(login)

        def update(self):
            self.sub_object.update()
        self.ndwy_thread.set_update(update)

        def delete(self):
            self.sub_object.on_alive = False
            del self.sub_object
        self.ndwy_thread.set_delete(delete)

        self.ndwy_thread.run()
        self.thread_pool.append(self.ndwy_thread)

    def email_timely(self):
        '''
            发送即时邮件
        '''

        self.email_timely_thread = subthread('发送即时邮件',
                                             self.email_timely_duration, self.log)
        def update(self):
            # 创建搜索和邮件发送对象
            users_obj = users()
            search_obj = search()
            server_obj = server()
            
            # 读取并更新时间戳
            timestamp = users_obj.db.last_update_time()
            users_obj.db.set_update_time(time.time())

            # 群发通知信息
            notice = search_obj.search_website(timestamp)
            for item in notice:
                server_obj.send_notice(item, users_obj.users, '通知')
            
            # 群发公众号消息
            notice = search_obj.search_wechat(timestamp)
            for item in notice:
                server_obj.send_notice(item, users_obj.users, '推文')
            
            del users_obj
            del search_obj
            del server_obj
        self.email_timely_thread.set_update(update)
        self.email_timely_thread.run()
        self.thread_pool.append(self.email_timely_thread)
    
    def email_ndwy(self):
        '''
            发送五育邮件
        '''

        self.email_ndwy_thread = subthread('发送五育邮件',
                                           self.email_ndwy_duration, self.log)
        
        def update(self):
            # 创建搜索和邮件发送对象
            users_obj = users()
            search_obj = search()
            server_obj = server()
            
            # 个性化推送五育消息
            for user in users_obj.users:
                wy = search_obj.search_ndwy(user)
                if len(wy) > 0:
                    server_obj.send_ndwy_list(user, wy)
                else:
                    self.log.write(f'''{user['name']} 无匹配五育活动！''', 'I')
            
            del users_obj
            del search_obj
            del server_obj
        self.email_ndwy_thread.set_update(update)
        self.email_ndwy_thread.run()
        self.thread_pool.append(self.email_ndwy_thread)

    def main(self)->None:
        '''
            运行爬虫，进行筛选，发送邮件
        '''
        
        try:
            # 开启子线程
            self.update_wechat()
            self.update_notice()
            self.update_ndwy()
            self.email_timely()
            self.email_ndwy()

            while True:
                print('请输入需要进行的操作：')
                print('query: 查看线程运行状态')
                print('toggle <id>: 启动/关闭子线程')
                print('restart <id>: 强制重启子线程')
                print('exit: 强制停止并关闭程序')

                try:
                    operate = input('').split(' ')
                    if operate[0] == 'query':
                        for i in range(0, len(self.thread_pool)):
                            print(self.thread_pool[i].get_status(i))
                    elif operate[0] == 'toggle':
                        id = int(operate[1])
                        if self.thread_pool[id].active:
                            self.thread_pool[id].quit()
                        else: self.thread_pool[id].run()
                    elif operate[0] == 'restart':
                        id = int(operate[1])
                        self.thread_pool[id].restart()
                    elif operate[0] == 'exit':
                        for thread in self.thread_pool:
                            if thread.active:
                                thread.quit()
                            if thread.sub_object \
                                and thread.sub_object.__dict__.get('on_alive'):
                                thread.sub_object.on_alive = False
                        break
                    else:
                        raise Exception('操作不存在！')
                except Exception as err:
                    print(f'操作出现错误：{err}')
        except KeyboardInterrupt:
            for thread in self.thread_pool:
                if thread.active:
                    thread.quit()

if __name__ == '__main__':
    a = breaker()
    a.main()