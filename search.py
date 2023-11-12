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
    website_list = []
    ndwy_list = []

    def __init__(self):
        # 打开通知数据库
        for table_name in self.website_dict:
            self.website_dict[table_name]['database'] = \
                self.load_database(table_name)

        # 打开五育数据库
        self.ndwy_database = self.load_database('ndwy')
        # 读取五育系统信息
        db_list = self.ndwy_database.findall()
        for item in db_list:
            if item[1] == 'utime':
                continue
            self.ndwy_list.append(json.loads(item[0]))

    @staticmethod
    def load_database(name):
        return database_sqlite.database(name)

    def search_website(self, timestamp):
        result_list = []
        for table_name in self.website_dict:
            ret = self.website_dict[table_name]['database'].search_by_timestamp(timestamp)

            for item in ret:
                item = json.loads(item[0])
                item['source'] = table_name
                result_list.append(item)
        return result_list

    @staticmethod
    def time_in_week(timestamp):
        time_struct = time.localtime(timestamp)
        weekday = time_struct.tm_wday
        hour = time_struct.tm_hour
        minute = time_struct.tm_min
        second = time_struct.tm_sec
        return weekday * 86400.0 + hour * 3600.0 + minute * 60.0 + second

    @staticmethod
    def time_in_day(timestamp):
        time_struct = time.localtime(timestamp)
        hour = time_struct.tm_hour
        minute = time_struct.tm_min
        second = time_struct.tm_sec
        return hour * 3600.0 + minute * 60.0 + second

    # 按照周几啥时间有空进行匹配。双指针实现，时间复杂度为 O(n*log2(n))
    # busy_time 以周为单位，有 3 个值 [weekday(0-6), start_time(0-86399), end_time(0-86399)]
    def search_by_week(self, item_list, busy_time, time_span):
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

    # 按照那天啥时候有空进行匹配。双指针实现，时间复杂度为 O(n*log2(n))
    # busy_time 以具体时间为单位，有 2 个值 [start_time_stamp, end_time_stamp]
    @staticmethod
    def search_by_date(item_list, busy_time, time_span):
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
    def search_by_valid(item_list, time_stamp):
        result_list = []
        for item in item_list:
            if item['details']['register'][1] > time_stamp \
                    and item['details']['active'][1] > time_stamp:
                result_list.append(item)

        return result_list

    @staticmethod
    def search_by_key_words(item_list, key_words):
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
    def search_by_type(item_list, project_type):
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

    # time_span 在项目开始/结束时间前加入预留时间（秒）
    # week_busy_time 一周什么时候没空
    # date_busy_time 特定的没空日期时间
    # key_words 关键词，之间是“或”关系
    # project_type 项目类型，劳、智等
    # valid 是否过滤报名结束，或已结束活动
    def search_ndwy(self, time_span=None,
                    week_busy_time=None, date_busy_time=None,
                    key_words=None, project_type=None,
                    valid=True):

        if time_span is None:
            time_span = [0.0, 0.0]

        result_list = self.ndwy_list
        if valid:
            result_list = self.search_by_valid(result_list, time.time())
        if key_words and len(key_words) > 0:
            result_list = self.search_by_key_words(result_list, key_words)
        if project_type and len(project_type) > 0:
            result_list = self.search_by_type(result_list, project_type)
        if week_busy_time and len(week_busy_time) > 0:
            result_list = self.search_by_week(result_list, week_busy_time, time_span)
        if date_busy_time and len(date_busy_time) > 0:
            result_list = self.search_by_date(result_list, week_busy_time, time_span)

        result_list = sorted(result_list, key=lambda x: x['details']['active'][0], reverse=False)
        return result_list

    # 打印
    def print_website_item(self, item):
        print('消息：', item['title'])
        print('标签：', ' | '.join(item['tag']))
        print('发布时间：', time.strftime(self.ndwy_database.time_format, time.localtime(item['rtime'])))
        print('链接：', item['href'])

    def print_ndwy_item(self, item, detail=True):
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


if __name__ == '__main__':
    search_object = search()
    res = search_object.search_ndwy()
    print(res)
    # res = search_object.search_website(time.time())
    # for i in res:
    #     search_object.print_website_item(i)
    #     print()
