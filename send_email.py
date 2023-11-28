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
            读取 HTML 模板，与邮箱建立连接
        '''

        # 读取 HTML 模板
        with open('./html/email-body-linear.html', 'r', encoding='utf-8') as file:
            self.ndwy_html_body = file.read()
        with open('./html/email-li-linear.html', 'r', encoding='utf-8') as file:
            self.ndwy_html_item = file.read()
        with open('./html/notice-body-linear.html', 'r', encoding='utf-8') as file:
            self.notice_html = file.read()
        
        # 建立邮箱对象
        self.smtp = smtplib.SMTP()
        self.smtp.connect(self.host, 25)
        self.smtp.login(self.username, self.password)

    def send_email(self, title: str, content: str, receiver:list)->None:
        '''
            发送邮件

            title: 邮件名
            content: 邮件正文
            receiver: 接收者列表
        '''
        
        print(f'send email "{title}" to {receiver}')
        return 

        message = MIMEMultipart()
        message['Subject'] = Header(title, 'utf-8')
        message['From'] = Header('NOVA', 'utf-8')
        message.attach(MIMEText(content, 'html', 'utf-8'))

        self.smtp.sendmail(self.username, receiver, message.as_string())
        # print('The email has been sent successfully!')

    def send_notice(self, item:dict, users:list, type:str)->None:
        '''
            逐条群发，推送通知消息

            item: 消息数据
            users: 指定的接收者列表
            type: 通知类型（通知/推文）
        '''
    
        content = self.notice_html
        content = content.format(source=item['source'],
            rtime=time.strftime(r'%Y年%m月%d日 %H:%M',
                                time.localtime(item['rtime'])),
            type=type, title=item['title'], href=item['href'],
            utime=time.strftime(r'%Y年%m月%d日 %H:%M', time.localtime()))
    
        for i in users:
            self.send_email(f'''NOVA 推送｜{type}：{item['title']}''',
                            content.replace('$$username$$', i['name']), i['email'])
    
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
        item_list = ''''''
        for item in items:
            li = self.ndwy_html_item

            active_time = self.format_time(item['details']['active'][0], item['details']['active'][1])
            register_time = self.format_time(item['details']['register'][0], item['details']['register'][1])
            
            li = li.format(name=item['title'],
                organiser=f'''{item['organiser']} - {item['details']['department']}''',
                type=item['details']['type'][0],
                span='{:.1f}'.format(item['details']['span']
                                     if item['details']['span'] else 0),
                people=item['details']['people'],
                active_start_time=active_time[0],
                active_end_time=active_time[1],
                place=item['details']['place'],
                register_start_time=register_time[0],
                register_end_time=register_time[1],
                rlease=time.strftime(r'%Y年%m月%d日 %H:%M',
                                    time.localtime(item['rtime'])),
                content=item['details']['content'])
            
            item_list += li
        
        content = content.replace('$$username$$', user['name'])
        content = content.replace('$$items$$', item_list)
        content = content.replace('$$update$$',
            time.strftime(r'%Y年%m月%d日 %H:%M:%S', time.localtime()))
        self.send_email(title, content, [user['email']])

if __name__ == '__main__':
    import search
    a = server()
    b = search.search()
    a.send_notice({'title': 'QwQ你好', 'href': '#'}, {'name': 'QWQ', 'email': '231880291@smail.nju.edu.cn'}, '测试')
    a.send_ndwy_list({'name': 'QWQ', 'email': '231880291@smail.nju.edu.cn'}, b.search_ndwy(1699707728))
    # print(b.search_ndwy(1699707728))