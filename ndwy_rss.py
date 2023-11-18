# developed by byml
# describe: 通过 RSS 源，获取南大五育系统活动

import time
import json
import requests
from lxml import etree

import database_sqlite


# 南大劳育 RSS 网址
# https://ndwy.nju.edu.cn/dztml/rssAPI/hdgc
class ndwy_rss:
    name = '五育系统'
    table_name = 'ndwy'

    # 设置
    def __init__(self):
        '''
            打开对应数据库
        '''

        self.db = database_sqlite.database(self.table_name)

    @staticmethod
    def for_details(info:str)->dict:
        '''
            从 RSS 的 XML 文档树中获取有用的信息

            info: 字符串格式的 XML 文档树
        '''

        web_time_format = '%Y/%m/%d %H:%M'
        name_map = {
            '所属模块：': 'module',
            '发起单位：': 'department',
            '活动地点：': 'place',
            '活动内容：': 'content'
        }
        details = {
            'place': '无', 'content': '无',
            'module': '无', 'department': '无',
            'register': [0, 0], 'active': [0, 0],
            'type': [], 'people': 0, 'span': 0.0
        }

        info = etree.HTML(info)
        for items in info.xpath('//p'):
            item = items.xpath('./span[1]/text()')[0]
            text = items.xpath('./text()')

            match item:
                case '报名时间：':
                    if len(text):
                        text = text[0].split('至')
                        start_time = time.mktime(time.strptime(text[0], web_time_format))
                        end_time = time.mktime(time.strptime(text[1], web_time_format))

                        if start_time <= end_time:
                            details['register'] = [start_time, end_time]
                        else:
                            details['register'] = [end_time, start_time]
                case '活动时间：':
                    if len(text):
                        text = text[0].split('至')
                        start_time = time.mktime(time.strptime(text[0], web_time_format))
                        end_time = time.mktime(time.strptime(text[1], web_time_format))

                        if start_time <= end_time:
                            details['active'] = [start_time, end_time]
                        else:
                            details['active'] = [end_time, start_time]
                case '五育类型：':
                    details['type'] = text[0].split('/') if len(text) else []
                case '招募人数：':
                    details['people'] = int(text[0]) if len(text) else 0
                case '时长：':
                    details['span'] = float(text[0]) if len(text) else 0.0
                case _:
                    details[name_map[item]] = text[0] if len(text) else ''
        return details

    def update(self, start_time:float=None)->None:
        '''
            获取在给定时间戳之后新增的五育项目

            start_time: 给定时间戳，空则自动从数据库中读取
        '''

        # <pubDate>Fri, 20 Oct 2023 06:29:29 GMT</pubDate>
        web_time_format = r'%a, %d %b %Y %H:%M:%S %Z'
        timestamp = start_time if start_time else self.db.last_update_time()

        print('程序已启动，因网站数据量较大，用时可能较久，请耐心等待 (*￣︶￣*)')
        data = requests.get('https://ndwy.nju.edu.cn/dztml/rssAPI/hdgc').content
        data = etree.XML(data)
        print('RSS源下载成功，进入数据处理！')
        # 本地测试数据
        # with open('./wyxt.txt', 'r', encoding='utf-8') as f_input:
        #     data = ''.join(f_input.readlines())
        # data = etree.XML(data.encode('utf-8'))

        rss_update_time = time.mktime(
            time.strptime(data.xpath('//channel/pubDate/text()')[0], web_time_format))
        if timestamp >= rss_update_time:
            return

        web_project_list = data.xpath('//channel/item')
        for items in web_project_list:
            title = items.xpath('./title/text()')
            organiser = items.xpath('./author/text()')
            rtime = time.mktime(
                time.strptime(items.xpath('./pubDate/text()')[0], web_time_format))
            s_id = f'{title}{rtime}'

            if rtime >= timestamp:
                if not self.db.exist(s_id):
                    self.db.insert(s_id, json.dumps({
                        'title': title[0] if len(title) else '',
                        'organiser': organiser[0] if len(organiser) else '',
                        'details': self.for_details(items.xpath('./description/text()')[0]),
                        'rtime': rtime
                    }), rtime)
            else:
                break

        self.db.set_update_time(time.time())

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
            print('招募人数：', item['details']['people'])
        if detail:
            print('报名时间：',
                  time.strftime(self.db.time_format, time.localtime(item['details']['register'][0])),
                  '-',
                  time.strftime(self.db.time_format, time.localtime(item['details']['register'][1])))
        if detail:
            print('活动内容：', item['details']['content'])

    def print_self(self)->None:
        '''
            打印输出数据库中所有的五育项目
        '''

        print('名称：', self.name)
        print('更新时间：', time.strftime(self.db.time_format, time.localtime(
            self.db.last_update_time())))

        print('存储信息：')
        data_list = self.db.findall()
        for item in data_list:
            if item[1] == 'utime':
                continue

            self.print_item(json.loads(item[0]))
            print()


if __name__ == '__main__':
    a = ndwy_rss()
    a.update()
    # a.print_self()
