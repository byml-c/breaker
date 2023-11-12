import re
import requests
import time
import json

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import database_sqlite


class wechat:
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
        '南京大学就业': {
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
    name = '微信平台'
    table_name = 'wechat'
    cookies, token = '', 0

    # 设置
    def __init__(self):
        self.db = database_sqlite.database(self.table_name)
        self.login()

    def login(self):
        browser = webdriver.Chrome()
        browser.get('https://mp.weixin.qq.com/')

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
            cookies = ''''''
            for items in browser.get_cookies():
                cookies += f'''{items['name']}={items['value']};'''

            self.cookies = cookies
            print(self.cookies)
            print(self.token)
            print('登录成功！')
        except Exception as err:
            print(f'登录出错：{err}')


    def update(self, start_time=None):
        time_stamp = start_time if start_time else self.db.last_update_time()

        for source in self.subscribe_list.keys():
            start_index = 0

            print(f'{source}：开始爬取！')
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
                header = {
                    'Cookie': self.cookies,
                    'Sec-Ch-Ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.61'
                }

                # 网络爬虫
                data = requests.get(url=url, params=args, headers=header)\
                    .content.decode('utf-8')
                print('{}：网页数据包获取完成，数据包大小 {:.2f} KB。'.format(source, len(data)/1024))

                # 本地测试文件
                # with open('wechat.txt', 'r', encoding='utf-8') as f_input:
                #     data = f_input.readline()
                
                data = json.loads(data)
                for item in data['app_msg_list']:
                    title = item['title']
                    href = item['link']
                    release_time = float(item['update_time'])
                    s_id = f'{title}{release_time}'

                    if release_time > (time_stamp - 24*3600):
                        if not self.db.exist(s_id):
                            is_modify += 1
                            self.db.insert(s_id, json.dumps({
                                'source': source,
                                'href': href,
                                'title': title,
                                'rtime': release_time
                            }), release_time)
                
                print('{}：爬取 {}-{} 更新已完成，更新 {} 条信息！正在规避频率检测：'
                      .format(source, start_index, start_index+5, is_modify))
                for wait_time in range(5, 0, -1):
                    print(f'还需等待：{wait_time} 秒。')
                    time.sleep(1)
                
                if is_modify == 0:
                    break
            
            print(f'{source}：爬取已完成！正在规避频率检测：')
            for wait_time in range(5, 0, -1):
                print(f'还需等待：{wait_time} 秒。')
                time.sleep(1)
            print('规避完成！')
        
        self.db.set_update_time(time.time())
    
    def self_print(self):
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
    a.update(1697385600)
    a.self_print()

