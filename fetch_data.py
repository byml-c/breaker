from datetime import datetime
from seatable_api import Base
import users_database
import json

class users:
    users = []
    def __init__(self):
        self.db = users_database.user_database()
        self.api_token = "0f762d4ccc5580dc73917b16ad7df6b53d5399b8"
        self.server_url = "https://table.nju.edu.cn/"
        self.base = Base(self.api_token, self.server_url)
        self.base.auth()
        self.update()

    def update(self):
        '''
            更新用户数据，保存到 self.users 里面
        '''
        self.get_data()
        user_list = self.db.fetch_all()
        self.users = [{
            'name': i[0],
            'email': i[2],
            'wbtime': [
                [int(k) for k in j.split(' ')]
                    for j in json.loads(i[3])],
            'grade': str(i[4] if i[4] else 0),
            'academy': str(i[5] if i[5] else 0),
            'degree': str(i[6] if i[6] else 0),
            'dbtime': [],
            'kwords': [],
            'type': [],
            'valid': True,
            'tspan': [0, 0]
        } for i in user_list if i[1] != 'utime']

    @staticmethod
    def time_convert(busytime: str) -> str:
        weekday_mapping = {
            "周一": 0,
            "周二": 1,
            "周三": 2,
            "周四": 3,
            "周五": 4,
            "周六": 5,
            "周日": 6,
        }
        parts = busytime.split()
        weekday_str = parts[0]
        time_range = parts[1]

        weekday = weekday_mapping.get(weekday_str)
        start_time_str, end_time_str = time_range.split("-")
        # 将时间字符串转换为时间对象
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
        # 计算开始时间和结束时间的秒数表示
        start_seconds = start_time.hour * 3600 + start_time.minute * 60
        end_seconds = end_time.hour * 3600 + end_time.minute * 60
        return f"""{weekday} {start_seconds} {end_seconds}"""

    @staticmethod
    def academy_convert(academy: str) -> str:
        academy_mapping = {
            "文学院": "4010",
            "历史学院": "4020",
            "哲学系（宗教学系）": "4030",
            "新闻传播学院": "4040",
            "法学院": "4050",
            "商学院": "4060",
            "外国语学院": "4070",
            "政府管理学院": "4080",
            "信息管理学院": "4090",
            "社会学院": "4100",
            "数学系": "4110",
            "物理学院": "4120",
            "天文与空间科学学院": "4130",
            "化学化工学院": "4140",
            "计算机科学与技术系": "4150",
            "电子科学与工程学院": "4160",
            "现代工程与应用科学学院": "4170",
            "环境学院": "4180",
            "地球科学与工程学院": "4190",
            "地理与海洋科学学院": "4200",
            "大气科学学院": "4210",
            "生命科学学院": "4220",
            "医学院": "4230",
            "工程管理学院": "4240",
            "匡亚明学院": "4250",
            "海外教育学院": "4260",
            "软件学院": "4270",
            "建筑与城市规划学院": "4280",
            "马克思主义学院": "4290",
            "人工智能学院": "4300",
            "教育研究院": "4310",
            "艺术学院": "4320",
            "中美文化研究中心": "4350",
            "国际关系学院": "4450",
            "安邦书院": "4901",
            "秉文书院": "4902",
            "行知书院": "4903",
            "开甲书院": "4904",
            "有训书院": "4905",
            "毓琇书院": "4906",
            "健雄书院": "4907",
            "体育科学研究所": "9911",
            "国际关系研究院": "9912",
            "党委办公室": "1010",
            "纪委办公室": "1020",
            "巡察工作办公室": "1030",
            "党委组织部": "1040",
            "党委宣传部": "1050",
            "新闻中心": "1051",
            "校报编辑部": "1052",
            "党委统战部": "1060",
            "党委教师工作部": "1070",
            "党委研究生工作部": "1080",
            "党委学生工作部": "1090",
            "党委保卫部": "1100",
            "党委人民武装部": "1110",
            "离退休工作处": "1120",
            "工会": "1130",
            "共青团南京大学委员会": "1140",
            "校长办公室": "2010",
            "法制办公室": "2011",
            "人力资源处": "2030",
            "教师教学发展中心": "2041",
            "科学技术处": "2050",
            "社会科学处": "2060",
            "心理健康教育与研究中心": "2080",
            "研究生院": "2090",
            "学生就业指导中心": "2100",
            "创新创业与成果转化工作办公室": "2110",
            "国内合作办公室": "2111",
            "学科建设与发展规划办公室": "2120",
            "信息化建设与管理办公室": "2130",
            "国际合作与交流处(台港澳事务办公室)": "2160",
            "财务处": "2170",
            "招标办公室": "2171",
            "审计处": "2180",
            "资产管理处": "2190",
            "实验室与设备管理处": "2200",
            "保卫处": "2210",
            "基本建设处": "2220",
            "后勤服务集团": "2230",
            "发展委员会": "2240",
            "校友工作办公室": "2250",
            "苏州校区建设工作领导小组办公室": "2260",
            "苏州校区管理委员会": "2261",
            "鼓楼校区管理办公室": "2280",
            "本科生院": "2300",
            "本科生院思想政治教育中心": "2302",
            "本科生院学生发展支持中心": "2303",
            "本科生院教学运行服务中心": "2304",
            "本科生院教育教学发展与评估中心": "2305",
            "本科生院综合办公室": "2307",
            "终身教育学院": "2320",
            "苏州校区": "2340",
            "图书馆": "3010",
            "信息化建设管理服务中心": "3011",
            "中国社会科学研究评价中心": "3020",
            "档案馆、校史博物馆": "3030",
            "南京大学博物馆": "3040",
            "学报编辑部": "3060",
            "教育技术中心": "3080",
            "现代分析中心": "3090",
            "南京大学医院": "3110",
            "大学外语部": "4330",
            "体育部": "4340",
            "模式动物研究所": "4360",
            "中国思想家研究中心": "4370",
            "中国南海研究协同创新中心": "4380",
            "人文社会科学高级研究院": "4410",
            "新生学院": "2310",
        }
        code = academy_mapping.get(academy)
        return code
    
    @staticmethod
    def degree_convert(degree: str)->str:
        degree_mapping = {
            "本科生": "211"
        }
        code = degree_mapping.get(degree)
        return code

    def get_data(self) -> None:
        rows = self.base.query(
            "select name, email, busytime, grade, academy, degree from Table1"
        )
        print("The data have been fetched successfully!")
        for row in rows:
            if self.db.exist(row['email']) == False:
                times = []
                for time in row["busytime"]:
                    times.append(self.time_convert(time))
                academy = self.academy_convert(row["academy"])
                degree = self.degree_convert(row['degree'])

                self.db.insert(
                    row["name"],
                    row["email"],
                    times,
                    row["grade"],
                    academy,
                    degree,
                )
                print("The data have been added to the database successfully!")


if __name__ == "__main__":
    a = users()
    # a.db.remove_database()
    a.update()
    print(a.users)