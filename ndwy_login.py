import re
import json
import time
import pickle
import requests
from lxml import etree
from threading import Thread

import authserve
import database_sqlite
from log import logger

class ndwy_login:
    session = None
    name = '五育系统-登录'
    table_name = 'ndwy_login'
    web_time_format = r'%Y-%m-%dT%H:%M:%S.000+0000'
    web_time_zone = 8 * 60 * 60

    on_alive = False
    alive_span = 30*10
    
    # 设置
    def __init__(self, online:bool=False):
        '''
            打开对应数据库，并进行登录

            online: 是否调用付费 OCR API 识别验证码
        '''

        self.online = online
        self.log = logger('ndwy')
        self.db = database_sqlite.database(self.table_name)
    
    def auto_login(self):
        with open('./data/ndwy.pkl', 'rb') as file:
            content = file.read()
            if content == b'':
                self.login()
            else:
                content = pickle.loads(content)
                self.session = requests.Session()
                self.session.cookies.update(content['cookies'])
                self.session.auth = content['auth']
                self.session.headers = content['headers']
                self.log.write('参数设置成功！', 'I')

                if not self.on_alive:
                    # 开启子线程，持续运行异步保活函数
                    self.alive_thread = Thread(target=self.run_alive)
                    self.alive_thread.start()

    def login(self):
        try:
            authserve_data = authserve.login()
            authserve_data.login(self.online)

            self.session = authserve_data.session
            # 本地留存
            with open('./data/ndwy.pkl', 'wb') as file:
                pickle.dump({
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
                    raise Exception('登录过期')
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
            url = f'http://ndwy.nju.edu.cn/'
            content = self.session.get(url).content.decode('utf-8')
            if re.search('统一身份认证', content):
                return False
            else:
                return True
        except Exception as err:
            self.log.write(f'保持活跃失败！错误：{err}', 'E')
            return False

    def for_details(self, item:dict)->dict:
        '''
            从数据中摘取有用的信息

            item: 完整的数据
        '''

        return {
            'place': item['hddd'],
            'content': item['nrjj'],
            'module': item['ssmk'],
            'department': item['fzrdw']['mc'],
            'register': [
                time.mktime(
                    time.strptime(item['bmks'], self.web_time_format)) + self.web_time_zone,
                time.mktime(
                    time.strptime(item['bmjs'], self.web_time_format)) + self.web_time_zone
            ],
            'active': [
                time.mktime(
                    time.strptime(item['xmks'], self.web_time_format)) + self.web_time_zone,
                time.mktime(
                    time.strptime(item['xmjs'], self.web_time_format)) + self.web_time_zone
            ],
            'type': item['wylx'].split('/'),
            'people': item.get('zmrs', 0),
            'span': item.get('sc', 0.0),

            'principle': {
                'name': item['fzrxm'],
                'phone': item['lxfs'],
                'email': item['mail']
            },
            'valid':{
                'academy': item['kcyxy'].split(','),
                'grade': item['kcynj'].split(','),
                'degree': item['kcyxl'].split(',')
            },
            'describe': item['khbf'],
            'area': item['xqs'].split(',') if item['xqs'] else [],
            'registed': item.get('bmrs', 0),
            'register_way': item['bmfs']['label']
        }
        
    def update(self, start_time:float=None)->None:
        '''
            获取在给定时间戳之后新增的五育项目

            start_time: 给定时间戳，空则自动从数据库中读取
        '''

        timestamp = start_time if start_time else self.db.last_update_time()

        # 状态说明：yrz(预热中), zmz(招募中)
        status_dict = ['yrz', 'zmz']
        for status in status_dict:
            list_url = f'https://ndwy.nju.edu.cn/dztml/rt/hdzx/ajaxList?state={status}&mc=&fzrdw=&page=1&limit=20&.me=YWFmMzQ1ZDEtMjQyMS00MGU5LWEyNTctZGQ3NzMyY2JlNTA4'
            data = self.session.get(list_url).content.decode('utf-8')
            data = json.loads(data)

            # 写入本地备份
            # with open(f'ndwy_{status}.txt', 'w', encoding='utf-8') as f_output:
            #     f_output.write(json.dumps(data))

            # 读取本地测试文件
            # with open(f'ndwy_{status}.txt', 'r', encoding='utf-8') as f_input:
            #     data = json.loads(f_input.readline())
            
            # 数据中的时间是 UTC+0
            for item in data['data']:
                title = item['mc']
                rtime = time.mktime(
                    time.strptime(item['czsj'], self.web_time_format)) + self.web_time_zone
                s_id = f'{title}{rtime}'

                if rtime >= timestamp:
                    if not self.db.exist(s_id):
                        self.db.insert(s_id, json.dumps({
                            'title': title,
                            'organiser': item['fzrdw']['mc'],
                            'details': self.for_details(item),
                            'rtime': rtime
                        }), rtime)
    
    def print_item(self, item:dict, detail:bool=True)->None:
        '''
            打印一则五育项目

            item: 项目数据
            detail: 是否输出较多细节
        '''
        
        print('名称：', item['title'])
        if detail:
            print('组织者-发起单位：', item['organiser'], '-', item['details']['department'])
        if detail:
            print('发布时间：', time.strftime(self.db.time_format, time.localtime(item['rtime'])))
        if detail:
            print('五育类型：', '/'.join(item['details']['type']))
        if detail:
            print('记录时长：', item['details']['span'])
        print('活动时间：',
              time.strftime(self.db.time_format, time.localtime(item['details']['active'][0])),
              '-',
              time.strftime(self.db.time_format, time.localtime(item['details']['active'][1])))
        print('活动地点：', item['details']['place'])
        if detail:
            print('招募人数-已经报名：', item['details']['people'],
                  '-', item['details']['registed'])
        if detail:
            print('报名时间：',
                  time.strftime(self.db.time_format, time.localtime(item['details']['register'][0])),
                  '-',
                  time.strftime(self.db.time_format, time.localtime(item['details']['register'][1])))
        if detail:
            print('活动内容：', item['details']['content'])


if __name__ == '__main__':
    try:
        a = ndwy_login(1)
        a.auto_login()
        # a.login()
        a.update()
    except KeyboardInterrupt:
        a.close_alive()