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
    def __init__(self):
        self.db = database_sqlite.database(self.table_name)
        self.authserve = authserve.login()
        self.authserve.login(0)

    def for_details(self, item):
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
        
    def update(self, start_time=None):
        time_stamp = start_time if start_time else self.db.last_update_time()

        # 状态说明：yrz(预热中), zmz(招募中)
        status_dict = ['yrz', 'zmz']
        for status in status_dict:
            list_url = f'https://ndwy.nju.edu.cn/dztml/rt/hdzx/ajaxList?state={status}&mc=&fzrdw=&page=1&limit=20&.me=YWFmMzQ1ZDEtMjQyMS00MGU5LWEyNTctZGQ3NzMyY2JlNTA4'
            data = self.authserve.session.get(list_url).content.decode('utf-8')
            data = json.loads(data)

            with open(f'ndwy_{status}.txt', 'w', encoding='utf-8') as f_output:
                f_output.write(json.dumps(data))

            # 读取本地测试文件
            # with open(f'ndwy_{status}.txt', 'r', encoding='utf-8') as f_input:
            #     data = json.loads(f_input.readline())
            
            # 数据中的时间是 UTC+0
            for item in data['data']:
                title = item['mc']
                rtime = time.mktime(
                    time.strptime(item['czsj'], self.web_time_format)) + self.web_time_zone
                s_id = f'{title}{rtime}'

                if rtime >= time_stamp:
                    if not self.db.exist(s_id):
                        self.db.insert(s_id, json.dumps({
                            'title': title,
                            'organiser': item['fzrdw']['mc'],
                            'details': self.for_details(item),
                            'rtime': rtime
                        }), rtime)
    
    def print_item(self, item, detail=True):
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
    a = ndwy_login()
    a.update()

'''
"data": [
        {
            "label": "文学院",
            "value": "4010"
        },
        {
            "label": "历史学院",
            "value": "4020"
        },
        {
            "label": "哲学系（宗教学系）",
            "value": "4030"
        },
        {
            "label": "新闻传播学院",
            "value": "4040"
        },
        {
            "label": "法学院",
            "value": "4050"
        },
        {
            "label": "商学院",
            "value": "4060"
        },
        {
            "label": "外国语学院",
            "value": "4070"
        },
        {
            "label": "政府管理学院",
            "value": "4080"
        },
        {
            "label": "信息管理学院",
            "value": "4090"
        },
        {
            "label": "社会学院",
            "value": "4100"
        },
        {
            "label": "数学系",
            "value": "4110"
        },
        {
            "label": "物理学院",
            "value": "4120"
        },
        {
            "label": "天文与空间科学学院",
            "value": "4130"
        },
        {
            "label": "化学化工学院",
            "value": "4140"
        },
        {
            "label": "计算机科学与技术系",
            "value": "4150"
        },
        {
            "label": "电子科学与工程学院",
            "value": "4160"
        },
        {
            "label": "现代工程与应用科学学院",
            "value": "4170"
        },
        {
            "label": "环境学院",
            "value": "4180"
        },
        {
            "label": "地球科学与工程学院",
            "value": "4190"
        },
        {
            "label": "地理与海洋科学学院",
            "value": "4200"
        },
        {
            "label": "大气科学学院",
            "value": "4210"
        },
        {
            "label": "生命科学学院",
            "value": "4220"
        },
        {
            "label": "医学院",
            "value": "4230"
        },
        {
            "label": "工程管理学院",
            "value": "4240"
        },
        {
            "label": "匡亚明学院",
            "value": "4250"
        },
        {
            "label": "海外教育学院",
            "value": "4260"
        },
        {
            "label": "软件学院",
            "value": "4270"
        },
        {
            "label": "建筑与城市规划学院",
            "value": "4280"
        },
        {
            "label": "马克思主义学院",
            "value": "4290"
        },
        {
            "label": "人工智能学院",
            "value": "4300"
        },
        {
            "label": "教育研究院",
            "value": "4310"
        },
        {
            "label": "艺术学院",
            "value": "4320"
        },
        {
            "label": "中美文化研究中心",
            "value": "4350"
        },
        {
            "label": "国际关系学院",
            "value": "4450"
        },
        {
            "label": "安邦书院",
            "value": "4901"
        },
        {
            "label": "秉文书院",
            "value": "4902"
        },
        {
            "label": "行知书院",
            "value": "4903"
        },
        {
            "label": "开甲书院",
            "value": "4904"
        },
        {
            "label": "有训书院",
            "value": "4905"
        },
        {
            "label": "毓琇书院",
            "value": "4906"
        },
        {
            "label": "健雄书院",
            "value": "4907"
        },
        {
            "label": "体育科学研究所",
            "value": "9911"
        },
        {
            "label": "国际关系研究院",
            "value": "9912"
        },
        {
            "label": "党委办公室",
            "value": "1010"
        },
        {
            "label": "纪委办公室",
            "value": "1020"
        },
        {
            "label": "巡察工作办公室",
            "value": "1030"
        },
        {
            "label": "党委组织部",
            "value": "1040"
        },
        {
            "label": "党委宣传部",
            "value": "1050"
        },
        {
            "label": "新闻中心",
            "value": "1051"
        },
        {
            "label": "校报编辑部",
            "value": "1052"
        },
        {
            "label": "党委统战部",
            "value": "1060"
        },
        {
            "label": "党委教师工作部",
            "value": "1070"
        },
        {
            "label": "党委研究生工作部",
            "value": "1080"
        },
        {
            "label": "党委学生工作部",
            "value": "1090"
        },
        {
            "label": "党委保卫部",
            "value": "1100"
        },
        {
            "label": "党委人民武装部",
            "value": "1110"
        },
        {
            "label": "离退休工作处",
            "value": "1120"
        },
        {
            "label": "工会",
            "value": "1130"
        },
        {
            "label": "共青团南京大学委员会",
            "value": "1140"
        },
        {
            "label": "校长办公室",
            "value": "2010"
        },
        {
            "label": "法制办公室",
            "value": "2011"
        },
        {
            "label": "人力资源处",
            "value": "2030"
        },
        {
            "label": "教师教学发展中心",
            "value": "2041"
        },
        {
            "label": "科学技术处",
            "value": "2050"
        },
        {
            "label": "社会科学处",
            "value": "2060"
        },
        {
            "label": "心理健康教育与研究中心",
            "value": "2080"
        },
        {
            "label": "研究生院",
            "value": "2090"
        },
        {
            "label": "学生就业指导中心",
            "value": "2100"
        },
        {
            "label": "创新创业与成果转化工作办公室",
            "value": "2110"
        },
        {
            "label": "国内合作办公室",
            "value": "2111"
        },
        {
            "label": "学科建设与发展规划办公室",
            "value": "2120"
        },
        {
            "label": "信息化建设与管理办公室",
            "value": "2130"
        },
        {
            "label": "国际合作与交流处(台港澳事务办公室)",
            "value": "2160"
        },
        {
            "label": "财务处",
            "value": "2170"
        },
        {
            "label": "招标办公室",
            "value": "2171"
        },
        {
            "label": "审计处",
            "value": "2180"
        },
        {
            "label": "资产管理处",
            "value": "2190"
        },
        {
            "label": "实验室与设备管理处",
            "value": "2200"
        },
        {
            "label": "保卫处",
            "value": "2210"
        },
        {
            "label": "基本建设处",
            "value": "2220"
        },
        {
            "label": "后勤服务集团",
            "value": "2230"
        },
        {
            "label": "发展委员会",
            "value": "2240"
        },
        {
            "label": "校友工作办公室",
            "value": "2250"
        },
        {
            "label": "苏州校区建设工作领导小组办公室",
            "value": "2260"
        },
        {
            "label": "苏州校区管理委员会",
            "value": "2261"
        },
        {
            "label": "鼓楼校区管理办公室",
            "value": "2280"
        },
        {
            "label": "本科生院",
            "value": "2300"
        },
        {
            "label": "本科生院思想政治教育中心",
            "value": "2302"
        },
        {
            "label": "本科生院学生发展支持中心",
            "value": "2303"
        },
        {
            "label": "本科生院教学运行服务中心",
            "value": "2304"
        },
        {
            "label": "本科生院教育教学发展与评估中心",
            "value": "2305"
        },
        {
            "label": "本科生院综合办公室",
            "value": "2307"
        },
        {
            "label": "终身教育学院",
            "value": "2320"
        },
        {
            "label": "苏州校区",
            "value": "2340"
        },
        {
            "label": "图书馆",
            "value": "3010"
        },
        {
            "label": "信息化建设管理服务中心",
            "value": "3011"
        },
        {
            "label": "中国社会科学研究评价中心",
            "value": "3020"
        },
        {
            "label": "档案馆、校史博物馆",
            "value": "3030"
        },
        {
            "label": "南京大学博物馆",
            "value": "3040"
        },
        {
            "label": "学报编辑部",
            "value": "3060"
        },
        {
            "label": "教育技术中心",
            "value": "3080"
        },
        {
            "label": "现代分析中心",
            "value": "3090"
        },
        {
            "label": "南京大学医院",
            "value": "3110"
        },
        {
            "label": "大学外语部",
            "value": "4330"
        },
        {
            "label": "体育部",
            "value": "4340"
        },
        {
            "label": "模式动物研究所",
            "value": "4360"
        },
        {
            "label": "中国思想家研究中心",
            "value": "4370"
        },
        {
            "label": "中国南海研究协同创新中心",
            "value": "4380"
        },
        {
            "label": "人文社会科学高级研究院",
            "value": "4410"
        },
        {
            "label": "新生学院",
            "value": "2310"
        }'''
