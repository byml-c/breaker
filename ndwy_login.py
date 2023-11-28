import json
import time
import requests
from lxml import etree

import authserve
import database_sqlite

class ndwy_login:
    authserve = None
    name = '五育系统-登录'
    table_name = 'ndwy_login'
    web_time_format = r'%Y-%m-%dT%H:%M:%S.000+0000'
    web_time_zone = 8 * 60 * 60

    # 设置
    def __init__(self, online:bool=False):
        '''
            打开对应数据库，并进行登录

            online: 是否调用付费 OCR API 识别验证码
        '''

        self.db = database_sqlite.database(self.table_name)
        self.authserve = authserve.login()
        self.authserve.login(online)

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
            data = self.authserve.session.get(list_url).content.decode('utf-8')
            data = json.loads(data)
            
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