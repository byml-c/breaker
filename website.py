# developed by byml
# describe: 爬取南大本科生院、校团委通知网站消息

import json
import time
import requests
from lxml import etree
import database_sqlite


class website:
    def __init__(self, name:str, en_name:str, web:str):
        '''
            初始化有关信息，创建或打开对应数据库
        '''

        self.web = web
        self.name = name
        self.table_name = en_name
        self.db = database_sqlite.database(self.table_name)

    def update(self, start_time:float=None)->None:
        '''
            获取在给定时间戳之后新增的五育项目

            start_time: 给定时间戳
        '''

        page_id = 0
        web_time_format = r'%Y-%m-%d'
        time_stamp = start_time if start_time else self.db.last_update_time()

        while True:
            page_id += 1
            is_modify = False

            # print(f'正在处理第 {page_id} 页')

            url = f'{self.web}/ggtz/list{page_id}.psp'
            page = requests.get(url=url).content.decode('utf-8')
            tree = etree.HTML(page)
            lists = tree.xpath(r'//div[@id="wp_news_w6"]/ul/li')

            for items in lists:
                href = '{}{}'.format(self.web, items.xpath(r'.//span[@class="news_title"]/a/@href')[0])
                title = items.xpath(r'.//span[@class="news_title"]/a/@title')[0]
                tag = items.xpath(r'.//span[@class="wjj"]/div/text()')
                tag = tag[0].split('，') if len(tag) > 0 else []
                release_time = time.mktime(
                    time.strptime(items.xpath(r'.//span[@class="news_meta"]/text()')[0], web_time_format))
                s_id = f'{title}{release_time}'

                if release_time > (time_stamp - 24*3600):
                    if not self.db.exist(s_id):
                        is_modify = True
                        self.db.insert(s_id, json.dumps({
                            'href': href,
                            'title': title,
                            'tag': tag,
                            'rtime': release_time
                        }), release_time)

            if not is_modify:
                break

        self.db.set_update_time(time.time())

    def print_self(self)->None:
        '''
            打印输出数据库中所有的五育项目
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
            print('标签：', ' | '.join(item['tag']))
            print('发布时间：', time.strftime(self.db.time_format, time.localtime(item['rtime'])))
            print('链接：', item['href'])
            print()


if __name__ == '__main__':
    a = website('校团委', 'tuanwei', 'https://tuanwei.nju.edu.cn')
    # a.update()
    a.print_self()

    b = website('本科生院', 'bksy', 'https://jw.nju.edu.cn')
    # b.update()
    # b.read()
    b.print_self()
