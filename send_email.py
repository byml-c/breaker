import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time

import database_sqlite

class router:
    table_name = 'user'
    host = 'smtp.exmail.qq.com'
    username = '231880291@smail.nju.edu.cn'
    password = 'iymZfT335UvRRxVj'
    user = []

    def __init__(self):
        '''
            打开数据库，获取接收者数据
            读取 HTML 模板
        '''

        self.db = database_sqlite.database(self.table_name)
        self.read_user()

        # 读取 HTML 模板
        with open('./html/email-body-linear.html', 'r', encoding='utf-8') as file:
            self.ndwy_html_body = file.read()
        with open('./html/email-li-linear.html', 'r', encoding='utf-8') as file:
            self.ndwy_html_item = file.read()

    def read_user(self):
        '''
            读取用户数据
        '''

        self.user = [{'name': 'QwQ', 'address': '231880291@smail.nju.edu.cn'}]

    def send_email(self, title: str, content: str, receiver:list)->None:
        '''
            发送邮件

            title: 邮件名
            content: 邮件正文
            receiver: 接收者列表
        '''

        message = MIMEMultipart()
        message['Subject'] = Header(title, 'utf-8')
        message['From'] = Header('NOVA', 'utf-8')
        message.attach(MIMEText(content, 'html', 'utf-8'))

        smtp_object = smtplib.SMTP()
        smtp_object.connect(self.host, 25)
        smtp_object.login(self.username, self.password)
        smtp_object.sendmail(self.username, receiver, message.as_string())
        print('The email has been sent successfully!')

    def send_item(self, item:dict, users:list)->None:
        '''
            逐条群发，推送通知消息

            item: 通知消息数据
            users: 指定的接收者列表
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
        self.send_email(title, content, [i['address'] for i in users])
    
    # 统一推送
    def send_ndwy_list(self, user:dict, items:list)->None:
        '''
            向单个用户推送五育消息

            user: 发送给的用户的数据
            item: 五育消息数据列表
        '''

        title = 'NOVA推送: 五育系统'

        content = self.ndwy_html_body
        content = content.replace('$$username$$', user['name'])
        content = content.replace('$$update$$', 
                                  time.strftime(r'%Y年%m月%d日 %H:%M:%S', time.localtime()))

        item_list = ''''''
        for item in items:
            li = self.ndwy_html_item
            li = li.replace('$$name$$', item['title'])
            li = li.replace('$$organiser$$', f'''{item['organiser']} - {item['details']['department']}''')
            li = li.replace('$$type$$', item['details']['type'][0])
            li = li.replace('$$span$$', '{:.1f}'.format(item['details']['span']))
            li = li.replace('$$people$$', str(item['details']['people']))
            li = li.replace('$$active_start_time$$',
                            time.strftime(self.db.time_format,
                                          time.localtime(item['details']['active'][0])))
            li = li.replace('$$active_end_time$$',
                            time.strftime(self.db.time_format,
                                          time.localtime(item['details']['active'][1])))
            li = li.replace('$$place$$', item['details']['place'])

            item_list += li
        
        content = content.replace('$$items$$', item_list)
        content = content.replace('$$now_time$$',
                                  time.strftime(r'%Y年%m月%d日 %H:%M:%S', time.localtime()))
        self.send_email(title, content, [user['address']])

if __name__ == '__main__':
    import search
    a = router()
    b = search.search()
    a.send_ndwy_list({'name': 'CAC', 'address': '231880291@smail.nju.edu.cn'}, b.search_ndwy(1699707728))
    # print(b.search_ndwy(1699707728))