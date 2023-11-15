import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time

import database_sqlite

class router:
    table_name = 'email'
    host = 'smtp.exmail.qq.com'
    username = '231880291@smail.nju.edu.cn'
    password = 'iymZfT335UvRRxVj'
    receiver = []

    def __init__(self):
        '''
            打开数据库，获取接收者数据
        '''

        self.db = database_sqlite.database(self.table_name)
        self.read_receiver()

    def read_receiver(self):
        '''
            读取接收者
        '''

        self.receiver = ['231880291@smail.nju.edu.cn']

    def send_email(self, title: str, content: str)->None:
        '''
            发送邮件

            title: 邮件名
            content: 邮件正文
        '''

        message = MIMEMultipart()
        message['Subject'] = Header(title, 'utf-8')
        message['From'] = Header('NOVA', 'utf-8')
        message.attach(MIMEText(content, 'html', 'utf-8'))

        smtp_object = smtplib.SMTP()
        smtp_object.connect(self.host, 25)
        smtp_object.login(self.username, self.password)
        smtp_object.sendmail(self.username, self.receiver, message.as_string())
        print('The email has been sent successfully!')

    def send_item(self, item:dict)->None:
        '''
            逐条推送通知消息

            item: 通知消息数据
        '''

        title = f'''NOVA推送: {item['title']}'''
        item['rtime'] = time.strftime(r'%Y年%m月%d日',
                                      time.localtime(item['rtime']))
        content = f'''
            <p>{item['source']}在{item['rtime']}发布了新通知：</p>
            <p><a href={item['href']}>{item['title']}</a></p>
            <p>请及时查看嗷 (^-^)</p>
            <hr />
            <p style="text-align: right;">
                NOVA推送
                <br />
                {time.strftime(r'%Y年%m月%d日 %H:%M:%S', time.localtime())}
            </p>
        '''
        self.send_email(title, content)
    
    # 统一推送
    def send_ndwy_list(self, items:list)->None:
        '''
            集中推送五育消息

            item: 五育消息数据列表
        '''

        title = 'NOVA推送: 五育系统'

        content = '''
            <p>来看看有什么新的五育活动可以报名吧：</p>
            <ul>
        '''
        for item in items:
            li = '''<li>'''
            li += f'''<div class="title">{item['title']}</div>'''
            li += f'''组织者-发起单位：<div class="organiser">{item['organiser']} - {item['details']['department']}</div>'''
            li += f'''五育类型：<div class="type">{'/'.join(item['details']['type'])}</div>'''
            li += f'''记录时长：<div class="span">{item['details']['span']}</div>'''
            li += f'''活动时间：<div class="time">{
                time.strftime(self.db.time_format,
                              time.localtime(item['details']['active'][0]))}
            - {
                time.strftime(self.db.time_format,
                              time.localtime(item['details']['active'][1]))
            }</div>'''
            li += f'''招募人数：<div class="people">{item['details']['people']}</div>'''
            li += f'''报名时间：<div class="time">{
                time.strftime(self.db.time_format,
                              time.localtime(item['details']['register'][0]))}
            - {
                time.strftime(self.db.time_format,
                              time.localtime(item['details']['register'][1]))
            }</div>'''
            li += f'''活动内容：<div class="content">{item['details']['content']}</div>'''
            li += '</li>'

            content += li
        
        content += f'''
            </ul>
            <hr />
            <p style="text-align: right;">
                NOVA推送
                <br />
                {time.strftime(r'%Y年%m月%d日 %H:%M:%S', time.localtime())}
            </p>
        '''

        self.send_email(title, content)

if __name__ == '__main__':
    import search
    a = router()
    b = search.search()
    a.send_ndwy_list(b.search_ndwy(1699707728))
    # print(b.search_ndwy(1699707728))