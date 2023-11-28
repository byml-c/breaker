# developed by byml
# describe: 从数据库中筛选出时间戳之后更新的消息、符合条件的五育活动

import time
import json

import database_sqlite

class search:
    website_dict = {
        'bksy': {
            'name': '本科生院',
            'database': None
        },
        'tuanwei': {
            'name': '团委',
            'database': None
        }
    }
    ndwy_list = []

    def __init__(self):
        '''
            打开对应数据库，
            仅从五育系统数据库中读取全部信息（方便多次更换条件的匹配）
        '''

        # 打开通知数据库
        for table_name in self.website_dict.keys():
            self.website_dict[table_name]['database'] = \
                self.load_database(table_name)

        # 打开五育数据库
        self.ndwy_database = self.load_database('ndwy_login')
        # 读取五育系统信息
        db_list = self.ndwy_database.fetchall()
        for item in db_list:
            if item[0] == 'utime':
                continue
            self.ndwy_list.append(json.loads(item[1]))
        
        # 打开微信公众号数据库
        self.wechat_database = self.load_database('wechat')

    @staticmethod
    def load_database(name:str):
        '''
            创建数据库对象
        '''

        return database_sqlite.database(name)

    def search_wechat(self, timestamp:float, sources:list=[])->dict:
        '''
            对 wechat 类型（wechat.py）爬虫获取的数据进行筛选，
            返回指定公众号在给定时间戳之后更新的数据

            timestamp: 给定时间戳
            source: 指定公众号列表，为空则任意
        '''

        result_list = []
        ret = self.wechat_database.search_by_timestamp(timestamp)
        for item in ret:
            item = json.loads(item[0])
            if len(sources) < 1 or (item['source'] in sources):
                item['source'] += '公众号'
                result_list.append(item)
        return result_list

    def search_website(self, timestamp:float, websites:list=[])->dict:
        '''
            对 website 类型（website.py）爬虫获取的数据进行筛选，
            返回指定网站在给定时间戳之后更新的数据

            timestamp: 给定时间戳
            websites: 指定通知网站，为空则任意
        '''

        result_list = []
        for table_name in self.website_dict.keys():
            ret = self.website_dict[table_name]['database'].search_by_timestamp(timestamp)

            for item in ret:
                if item[0] == 'utime':
                    continue
                item = json.loads(item[1])
                item['source'] = self.website_dict[table_name]['name']
                if len(websites) < 1 or (item['source'] in websites):
                    result_list.append(item)
        return result_list

    @staticmethod
    def time_in_week(timestamp:float)->float:
        '''
            返回时间戳给定时间在该周中的相对时间：
            从 星期一00:00:00 为计时起点，以到 星期日23:59:59 为周期的时间

            timestamp: 给定时间戳
        '''

        time_struct = time.localtime(timestamp)
        weekday = time_struct.tm_wday
        hour = time_struct.tm_hour
        minute = time_struct.tm_min
        second = time_struct.tm_sec
        return weekday * 86400.0 + hour * 3600.0 + minute * 60.0 + second

    @staticmethod
    def time_in_day(timestamp:float)->float:
        '''
            返回时间戳给定时间在该日中的相对时间：
            从 00:00:00 为计时起点，以到 23:59:59 为周期的时间

            timestamp: 给定时间戳
        '''

        time_struct = time.localtime(timestamp)
        hour = time_struct.tm_hour
        minute = time_struct.tm_min
        second = time_struct.tm_sec
        return hour * 3600.0 + minute * 60.0 + second

    def search_by_week(self, item_list:list, busy_time:list, time_span:list)->list:
        '''
            按照周几什么时间没空进行匹配，返回没被卡掉的时间。
            双指针实现，时间复杂度为 O(n*log2(n))
            
            item_list: 待筛选的列表
            busy_time: 以周为单位，
                每一项有 3 个值 [weekday(0-6), start_time(0-86399), end_time(0-86399)]
            time_span: 有两个元素的列表，
                代表在一个活动前需要留出 time_span[0] 的时间，
                活动后需留出 time_span[1] 的时间，
                用来将通勤时间加入考虑范围
        '''

        unique_range = [[0, 0]]
        for b_id in range(0, len(busy_time), 1):
            item = busy_time[b_id]
            busy_time[b_id] = [item[0] * 86400.0 + item[1],
                               item[0] * 86400.0 + item[2]]

        busy_time = sorted(busy_time,
                           key=lambda x: (x[0], x[1]), reverse=False)
        item_list = sorted(item_list,
                           key=lambda x: self.time_in_week(x['details']['active'][0]),
                           reverse=False)

        for item in busy_time:
            if item[0] <= unique_range[-1][1]:
                unique_range[-1][1] = max(item[1], unique_range[-1][1])
            else:
                unique_range.append(item)

        result_list = []
        unique_index, unique_len = 0, len(unique_range)
        for item in item_list:
            start_time = self.time_in_week(item['details']['active'][0]) - time_span[0]
            end_time = self.time_in_week(item['details']['active'][1]) + time_span[1]

            while unique_index < unique_len \
                    and unique_range[unique_index][1] <= start_time:
                unique_index += 1

            if unique_index >= unique_len:
                result_list.append(item)
            elif unique_range[unique_index][0] >= end_time:
                result_list.append(item)

        return result_list

    @staticmethod
    def search_by_date(item_list:list, busy_time:list, time_span:list)->list:
        '''
            按照某一天什么时间没空进行匹配，返回没被卡掉的时间。
            双指针实现，时间复杂度为 O(n*log2(n))
            
            item_list: 待筛选的列表
            busy_time: 内为具体时间戳，有 2 个值 [start_time_stamp, end_time_stamp]
            time_span: 有两个元素的列表，
                代表在一个活动前需要留出 time_span[0] 的时间，
                活动后需留出 time_span[1] 的时间，
                用来将通勤时间加入考虑范围
        '''

        item_list = sorted(item_list, key=lambda x: x['details']['active'][0], reverse=False)

        unique_range = [[0, 0, 0]]
        busy_time = sorted(busy_time,
                           key=lambda x: x[0], reverse=False)
        for item in busy_time:
            if item[0] == unique_range[-1][0]:
                if item[1] <= unique_range[-1][2]:
                    unique_range[-1][2] = max(item[2], unique_range[-1][2])
                else:
                    unique_range.append(item)
            else:
                unique_range.append(item)

        result_list = []
        unique_index, unique_len = 0, len(unique_range)
        for item in item_list:
            time_range = item['details']['active']
            time_range[0] = time_range[0] - time_span[0]
            time_range[1] = time_range[1] + time_span[1]

            while unique_index < unique_len \
                    and unique_range[unique_index][1] <= time_range[0]:
                unique_index += 1

            if unique_index >= unique_len:
                result_list.append(item)
            elif unique_range[unique_index][0] >= time_range[1]:
                result_list.append(item)

        return result_list

    @staticmethod
    def search_by_valid(item_list, timestamp:float, academy:str, grade:str, degree:str)->str:
        '''
            去除不可报名、已经结束的活动
            
            item_list: 待筛选的列表
            timestamp: 只保留在该时间戳之后可报名、未开始的活动
            academy: 保留该学院可报名的项目
            grade: 保留该年级可报名的项目
            degree: 保留该学历可报名的项目
        '''

        result_list = []
        for item in item_list:
            if item['details']['register'][1] > timestamp \
                    and item['details']['active'][1] > timestamp:
                result_list.append(item)
        
        # 匹配对应学院
        if not (academy == '0'):
            item_list = result_list
            result_list = []

            for item in item_list:
                if len(item['details']['valid']['academy']) > 1:
                    if academy in item['details']['valid']['academy']:
                        result_list.append(item)
                else: result_list.append(item)

        # 匹配对应年级
        if not (grade == '0'):
            item_list = result_list
            result_list = []

            for item in item_list:
                if len(item['details']['valid']['grade']) > 1:
                    if grade in item['details']['valid']['grade']:
                        result_list.append(item)
                else: result_list.append(item)

        # 匹配对应学历
        if not (degree == '0'):
            item_list = result_list
            result_list = []

            for item in item_list:
                if len(item['details']['valid']['grade']) > 1:
                    if degree in item['details']['valid']['degree']:
                        result_list.append(item)
                else: result_list.append(item)

        return result_list

    @staticmethod
    def search_by_key_words(item_list:list, key_words:list)->list:
        '''
            返回含有关键词的列表，关键词之间是“或”关系
            
            item_list: 待筛选的列表
            key_words: 关键词列表
        '''

        result_list = []
        for item in item_list:
            is_match = False

            for words in key_words:
                if words in item['title']:
                    is_match = True
                    break

            if is_match:
                result_list.append(item)

        return result_list

    @staticmethod
    def search_by_type(item_list:list, project_type:list)->list:
        '''
            返回指定类型的项目，类型之间是“或”关系
            
            item_list: 待筛选的列表
            project_type: 类型列表
        '''
        result_list = []
        for item in item_list:
            is_match = False
            for t in project_type:
                if t == item['details']['type'][0]:
                    is_match = True
                    break
            if is_match:
                result_list.append(item)

        return result_list

    def search_ndwy(self, user)->list:
        '''
            整合筛选函数，返回符合条件的项目

            user: 用户数据

            tspan(time_span): 有两个元素的列表，
                代表在一个活动前需要留出 time_span[0] 的时间，
                活动后需留出 time_span[1] 的时间，
                用来将通勤时间加入考虑范围
            wbtime(week_busy_time): 一周什么时候没空
                每一项有 3 个值 [weekday(0-6), start_time(0-86399), end_time(0-86399)]
            dbtime(date_busy_time): 特定的没空日期时间
                内为具体时间戳，有 2 个值 [start_time_stamp, end_time_stamp]
            kwords(key_words): 关键词列表，之间是“或”关系
            type(project_type): 项目类型列表，劳、智等，之间是“或”关系
            valid: 是否过滤不可参加活动（报名结束，或已结束活动）
            academy: 用户所属学院
            grade: 用户所属年级，2021/2022 等
            degree: 用户学历
        '''
        
        result_list = self.ndwy_list
        
        if user['valid']:
            result_list = self.search_by_valid(result_list, time.time(),
                                               user['academy'], user['grade'], user['degree'])
        if user['kwords'] and len(user['kwords']) > 0:
            result_list = self.search_by_key_words(result_list, user['kwords'])
        if user['type'] and len(user['type']) > 0:
            result_list = self.search_by_type(result_list, user['type'])
        if user['wbtime'] and len(user['wbtime']) > 0:
            result_list = self.search_by_week(result_list, user['wbtime'], user['tspan'])
        if user['dbtime'] and len(user['dbtime']) > 0:
            result_list = self.search_by_date(result_list, user['dbtime'], user['tspan'])

        result_list = sorted(result_list, key=lambda x: x['details']['active'][0], reverse=False)
        return result_list

    def print_website_item(self, item:dict)->None:
        '''
            打印一则通知消息

            item: 消息数据
        '''

        print('消息：', item['title'])
        print('标签：', ' | '.join(item['tag']))
        print('发布时间：', time.strftime(self.ndwy_database.time_format, time.localtime(item['rtime'])))
        print('链接：', item['href'])

    def print_ndwy_item(self, item:dict, detail:bool=True)->None:
        '''
            打印一则五育项目

            item: 项目数据
            detail: 是否输出较多细节
        '''

        print('名称：', item['title'])
        if detail:
            print('组织者-发起单位：', item['organiser'], '-', item['details']['department'])
        if detail:
            print('发布时间：', time.strftime(self.ndwy_database.time_format, time.localtime(item['rtime'])))
        if detail:
            print('五育类型：', '/'.join(item['details']['type']))
        if detail:
            print('记录时长：', item['details']['span'])
        print('活动时间：',
              time.strftime(self.ndwy_database.time_format, time.localtime(item['details']['active'][0])),
              '-',
              time.strftime(self.ndwy_database.time_format, time.localtime(item['details']['active'][1])))
        print('活动地点：', item['details']['place'])
        if detail:
            print('招募人数：', item['details']['people'])
        if detail:
            print('报名时间：',
                  time.strftime(self.ndwy_database.time_format, time.localtime(item['details']['register'][0])),
                  '-',
                  time.strftime(self.ndwy_database.time_format, time.localtime(item['details']['register'][1])))
        if detail:
            print('活动内容：', item['details']['content'])