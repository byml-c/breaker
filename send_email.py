import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time

class server:
    table_name = 'user'
    host = 'smtp.exmail.qq.com'
    username = '231880291@smail.nju.edu.cn'
    password = 'iymZfT335UvRRxVj'
    user = []

    def __init__(self):
        '''
            读取 HTML 模板
        '''

        # 读取 HTML 模板
        with open('./html/email-body-linear.html', 'r', encoding='utf-8') as file:
            self.ndwy_html_body = file.read()
        with open('./html/email-li-linear.html', 'r', encoding='utf-8') as file:
            self.ndwy_html_item = file.read()

    def send_email(self, title: str, content: str, receiver:list)->None:
        '''
            发送邮件

            title: 邮件名
            content: 邮件正文
            receiver: 接收者列表
        '''

        print(f'send email "{title}" to {receiver}, content:\n{content}\n\n')
        # message = MIMEMultipart()
        # message['Subject'] = Header(title, 'utf-8')
        # message['From'] = Header('NOVA', 'utf-8')
        # message.attach(MIMEText(content, 'html', 'utf-8'))

        # smtp_object = smtplib.SMTP()
        # smtp_object.connect(self.host, 25)
        # smtp_object.login(self.username, self.password)
        # smtp_object.sendmail(self.username, receiver, message.as_string())
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
    
    def format_time(self, t1:float, t2:float)->list:
        '''
            给定两个时间戳，返回格式化的时间，
            不显示年，并去除重复项

            比如两个时间戳对应的是：
            t1: 2023.11.11 Sat 00:00:00
            t2: 2023.11.11 Sat 01:01:00
            则会返回：['11.11 星期六 00:00', '01:01']
        '''
        week_list = ['一', '二', '三', '四', '五', '六', '日']

        t1 = time.localtime(t1)
        ft1 = time.strftime(r'%m.%d 星期', t1) + week_list[t1.tm_wday]
        t2 = time.localtime(t2)
        ft2 = time.strftime(r'%m.%d 星期', t2) + week_list[t2.tm_wday]

        return [ft1 + time.strftime(r' %H:%M', t1),
                ('' if ft1 == ft2 else ft2+' ') + time.strftime(r'%H:%M', t2)]

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
            active_time = self.format_time(item['details']['active'][0], item['details']['active'][1])
            li = li.replace('$$active_start_time$$', active_time[0])
            li = li.replace('$$active_end_time$$', active_time[1])
            li = li.replace('$$place$$', item['details']['place'])
            register_time = self.format_time(item['details']['register'][0], item['details']['register'][1])
            li = li.replace('$$register_start_time$$', register_time[0])
            li = li.replace('$$register_end_time$$', register_time[1])
            li = li.replace('$$rlease$$', time.strftime(r'%Y年%m月%d日 %H:%M', time.localtime(item['rtime'])))
            li = li.replace('$$content$$', item['details']['content'])

            item_list += li
        
        content = content.replace('$$items$$', item_list)
        content = content.replace('$$now_time$$',
                                  time.strftime(r'%Y年%m月%d日 %H:%M:%S', time.localtime()))
        self.send_email(title, content, [user['address']])

if __name__ == '__main__':
    import search
    a = server()
    b = search.search()
    a.send_ndwy_list({'name': 'QWQ', 'address': '231880291@smail.nju.edu.cn'}, b.search_ndwy(1699707728))
    # print(b.search_ndwy(1699707728))