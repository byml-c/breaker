import re
import json
import base64
import requests
import urllib.parse
import database_sqlite

class login:
    session = None
    username = '**'
    password = '**'

    def need_captcha(self):
        need_url = f'https://authserver.nju.edu.cn/authserver/needCaptcha.html'
        res = self.session.post(need_url, data={'username': self.username})
        return 'true' in res.text

    def get_captch(self, online):
        if self.need_captcha():
            captch_url = 'https://authserver.nju.edu.cn/authserver/captcha.html'
            captch_img = self.session.get(captch_url).content

            # 本地存档一份当前验证码
            with open('chaptch.jpg', 'wb') as img_output:
                img_output.write(captch_img)

            if online:
                captch_img = 'data:image/jpg;base64,{}'.format(
                    base64.b64encode(captch_img).decode('utf-8'))
                
                data = {
                    'image': captch_img,
                    'token': '-aiEOVLTyt9yoOmq6cLvYrKejQGimynQieo3IjO1k44',
                    'type': 10110
                }
                res = self.session.post('http://api.jfbym.com/api/YmServer/customApi',
                                        data = data).content.decode('utf-8')
                res = json.loads(res)
                if res['code'] == 10000:
                    return res['data']['data']
                elif res['code'] == 10002:
                    print('欠费啦！')
                    return ''
                else:
                    return ''
            else:
                return input('请输入验证码：')
        else:
            return ''
        
    # 如果参数给 True，将调用付费验证码识别 api
    def login(self, online=False):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'})

        index_url = 'https://authserver.nju.edu.cn/authserver/login'
        index_page = self.session.get(index_url).content.decode('utf-8')

        password_seed = re.search(r'pwdDefaultEncryptSalt = \"(.*?)\"', index_page).group(1)     

        data = {'username': self.username, 'password': self.password, 'seed': password_seed}
        local_url = 'http://localhost:1117/login'
        res = requests.post(url=local_url, data=data)

        form = {
            'username': self.username,
            'password': res.text,
            'captchaResponse': self.get_captch(online),
            'lt': re.search(r'name="lt" value="(.*?)"', index_page).group(1),
            'execution': re.search(r'name="execution" value="(.*?)"', index_page).group(1),
            '_eventId': re.search(r'name="_eventId" value="(.*?)"', index_page).group(1),
            'rmShown': re.search(r'name="rmShown" value="(.*?)"', index_page).group(1),
            'dllt': 'userNamePasswordLogin',
        }
        
        login_url = 'https://authserver.nju.edu.cn/authserver/login'
        res = self.session.post(url=login_url, data=form, allow_redirects=False)
        
        if res.status_code == 302:
            print('Login successfully!')
        else:
            print('Login error!')

if __name__ == '__main__':
    a = login()
    a.login()
    
