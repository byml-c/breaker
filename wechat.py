import re
import time
import json
import pickle
import requests
from requests.cookies import RequestsCookieJar as CookieJar

from threading import Thread

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import database_sqlite
from log import logger

class wechat:
    # 订阅列表，每一个公众号有一个唯一的 fakeid
    subscribe_list = {
        '南京大学': {
            'fakeid': 'MzAxODAzMjQ1NQ=='
        },
        '南京大学信息门户': {
            'fakeid': 'MzU3OTU2MzY2NQ=='
        },
        '南京大学学生会': {
            'fakeid': 'MjM5MjY4NTY5NQ=='
        },
        '南大招生小蓝鲸': {
            'fakeid': 'MzA3NzQ2ODEwNQ=='
        },
        '南京大学医院': {
            'fakeid': 'MzU1MTU2OTE0OQ=='
        },
        '南京大学财务处': {
            'fakeid': 'MzUyNDUyMTgzNA=='
        },
        '南大就业': {
            'fakeid': 'MzUyNTE1MjQ3Mg=='
        },
        '南京大学图书馆': {
            'fakeid': 'MjM5NTE5Mjk1Mg=='
        },
        '南京大学苏州校区': {
            'fakeid': 'MzkyMjIxNzQ1Ng=='
        },
        '南京大学新生学院': {
            'fakeid': 'MzkwNDE4ODYyMg=='
        },
        '南京大学毓琇书院': {
            'fakeid': 'Mzg5MTU0NDIzOQ=='
        },
        '南京大学开甲书院': {
            'fakeid': 'Mzk0MjE5MDI5Nw=='
        },
        '南京大学健雄书院': {
            'fakeid': 'MzkwODQwMDEzNg=='
        }
    }
    name = '微信公众号'
    table_name = 'wechat'
    session, token = None, ''
    on_alive, scheduler = False, None
    alive_thread = None

    alive_span = 5*60 # 三分钟进行一次会话，保持与服务器的连接
    time_tag = 0
    freqency = 5 # 单次请求之间的间隔秒数

    # 设置
    def __init__(self):
        '''
            打开数据库、日志
        '''
        
        self.log = logger('wechat')
        self.db = database_sqlite.database(self.table_name)
    
    def __del__(self):
        '''
            析构函数，负责关闭子线程、日志
        '''

        self.close_alive()

    def auto_login(self)->None:
        '''
            如果 session 数据存在，直接设置 session 对象
            否则调用登录模块
        '''

        with open('./data/wechat.pkl', 'rb') as file:
            content = file.read()
            if content == b'':
                self.login()
                return True
            else:
                content = pickle.loads(content)
                self.session = requests.Session()
                self.session.cookies.update(content['cookies'])
                self.session.auth = content['auth']
                self.session.headers = content['headers']
                self.token = content['token']
                self.log.write('参数设置成功！', 'I')

                # 先测试是否登录成功
                if not self.keep_alive():
                    return False
                
                if not self.on_alive:
                    # 开启子线程，持续运行异步保活函数
                    self.alive_thread = Thread(target=self.run_alive)
                    self.alive_thread.start()
                
                # 成功启动则返回 True
                return True

    def login(self):
        '''
            调用 selenium 框架进行登录，
            需要手机微信扫码登录账号，

            登录后获得 self.token 和创建 self.session
        '''

        browser = webdriver.Chrome()
        browser.get('https://mp.weixin.qq.com/')

        self.session = requests.Session()
        self.session.__exit__ = None
        self.session.headers.update({
            'Sec-Ch-Ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.61'
        })

        try:
            wait = WebDriverWait(browser, 30)
            enter = wait.until(
                EC.presence_of_element_located((By.ID, 'js_mp_sidemenu'))
            )
            
            self.token = re.search(r'token=(\d+)', browser.current_url).group(1)
            new_url = f'https://mp.weixin.qq.com/cgi-bin/appmsg? \
                t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=0&token={self.token}&lang=zh_CN'
            browser.get(new_url)
            enter = wait.until(
                EC.presence_of_element_located((By.ID, 'js_editor_insertlink'))
            )

            selenium_cookies = browser.get_cookies()
            cookies = CookieJar()
            for item in selenium_cookies:
                cookies.set(item['name'], item['value'])
            self.session.cookies.update(cookies)
            
            # 本地留存
            with open('./data/wechat.pkl', 'wb') as file:
                pickle.dump({
                    'token': self.token,
                    'cookies': self.session.cookies.get_dict(),
                    'auth': self.session.auth,
                    'headers': self.session.headers
                }, file)
            self.log.write('登录成功！', 'I')

            if not self.on_alive:
                # 开启子线程，持续运行异步保活函数
                self.alive_thread = Thread(target=self.run_alive)
                self.alive_thread.start()
        except Exception as err:
            self.on_alive = False
            raise Exception(f'登录出错：{err}')

    def run_alive(self):
        '''
            初始化定时保活模块
        '''

        self.log.write('活跃保持已开启', 'I')
        self.on_alive = True
        time_accumulate = self.alive_span
        while self.on_alive:
            if time_accumulate >= self.alive_span:
                if not self.keep_alive():
                    self.log.write('登录过期！', 'E')
                    self.on_alive = False
                    break
                else:
                    self.log.write('保持活跃中！', 'I')
                time_accumulate = 0
            else: time_accumulate += 1
            time.sleep(1)
        self.log.write('活跃保持已关闭', 'I')

    def close_alive(self):
        self.on_alive = False

    def keep_alive(self):
        '''
            子线程定时调用此函数，与服务器交互，
            保持登录状态，检测 session 是否过期
        '''

        try:
            url = f'https://mp.weixin.qq.com/cgi-bin/appmsg? \
                t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=0&token={self.token}&lang=zh_CN'
            
            if re.search(r'请重新', self.session.get(url).content.decode('utf-8')):
                return False
            else:
                return True
        except Exception as err:
            self.log.write(f'保持活跃失败！错误：{err}', 'E')
            return False

    def update(self, start_time:float=None)->None:
        '''
            爬虫更新公众号消息

            start_time: 开始时间戳（不给则从数据库中读取）
        '''

        timestamp = start_time if start_time else self.db.last_update_time()

        for source in self.subscribe_list.keys():
            start_index = -5

            self.log.write(f'公众号 {source}：开始爬取！')
            while True:
                is_modify = 0
                start_index += 5

                url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
                args = {
                    'action': 'list_ex',
                    'begin': start_index,
                    'count': 5,
                    'fakeid': self.subscribe_list[source]['fakeid'],
                    'type': 9, 'query': '',
                    'token': self.token,
                    'lang': 'zh_CN', 'f': 'json', 'ajax': 1
                }

                # 爬虫

                while True:
                    if not self.on_alive: break
                    if time.time() - self.time_tag >= self.freqency:
                        # 保证每次访问间隔至少 freqency 秒
                        data = self.session.get(url=url, params=args).content.decode('utf-8')
                        self.time_tag = time.time()
                        break
                    else: time.sleep(1)

                # 强制终止
                if not self.on_alive: break

                data = json.loads(data)
                if not (data['base_resp']['err_msg'] == 'ok'):
                    if data['base_resp']['err_msg'] == 'invalid session':
                        self.log.write('登录过期！', 'E')
                        raise Exception('登录过期')
                    elif data['base_resp']['err_msg'] == 'freq control':
                        self.log.write('由于访问过于频繁，接口失效！', 'E')
                        raise Exception('接口失效')
                    else:
                        self.log.write(f'''服务器返回错误：{data['base_resp']['err_msg']}''', 'E')
                else:
                    # print('{}：网页数据包获取完成，数据包大小 {:.2f} KB。'
                    #       .format(source, len(data)/1024))

                    # 本地测试文件
                    # with open('wechat.txt', 'r', encoding='utf-8') as f_input:
                    #     data = f_input.readline()
                    
                    try:
                        for item in data['app_msg_list']:
                            title = item['title']
                            href = item['link']
                            release_time = float(item['update_time'])
                            s_id = f'{title}{release_time}'

                            if release_time > (timestamp - 24*3600) and (not self.db.exist(s_id)):
                                is_modify += 1
                                self.db.insert(s_id, json.dumps({
                                    'source': source,
                                    'href': href,
                                    'title': title,
                                    'rtime': release_time
                                }), release_time)
                                self.log.write(f'''{source} 更新推文：{title}''', 'I')
                    except Exception as err:
                        self.log.write(f'公众号 {source} 爬取出错，错误：{err}', 'W')
                
                if is_modify == 0:
                    break
            
            if self.on_alive:
                self.log.write(f'''{source}：爬取已完成！''')
            else:
                self.log.write(f'''{source}： 强制终止！''')
                break
        
        if self.on_alive:
            self.db.set_update_time(time.time())
            self.log.write('更新完成！', 'I')
        else:
            self.log.write('强制终止！', 'I')
    
    def self_print(self):
        '''
            打印输出数据库内全部信息
        '''

        print('名称：', self.name)
        print('更新时间：', time.strftime(self.db.time_format, time.localtime(self.db.last_update_time())))

        print('存储信息：')
        data_list = self.db.findall()
        for item in data_list:
            if item[1] == 'utime':
                continue

            item = json.loads(item[0])
            print('消息：', item['title'])
            print('来源：', item['source'])
            print('发布时间：', time.strftime(self.db.time_format, time.localtime(item['rtime'])))
            print('链接：', item['href'])
            print()


if __name__ == '__main__':
    a = wechat()
    a.login()
