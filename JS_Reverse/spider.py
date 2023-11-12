import re
import json
import requests

class authserve_login:
    session = None
    username = '231880291'
    password = 'cbj117@THr'

    def need_captcha(self):
        need_url = f'https://authserver.nju.edu.cn/authserver/needCaptcha.html'
        res = self.session.post(need_url, data={'username': self.username})
        return 'true' in res.text

    def get_captch(self):
        if self.need_captcha():
            captch_url = 'https://authserver.nju.edu.cn/authserver/captcha.html'
            captch_img = self.session.get(captch_url).content
            with open('chaptch.jpg', 'wb') as img_output:
                img_output.write(captch_img)
            return input('请输入验证码：')
        else:
            return ''
        
    def login(self):
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
            'captchaResponse': self.get_captch(),
            'lt': re.search(r'name="lt" value="(.*?)"', index_page).group(1),
            'execution': re.search(r'name="execution" value="(.*?)"', index_page).group(1),
            '_eventId': re.search(r'name="_eventId" value="(.*?)"', index_page).group(1),
            'rmShown': re.search(r'name="rmShown" value="(.*?)"', index_page).group(1),
            'dllt': 'userNamePasswordLogin',
        }
        print(form)
        login_url = 'https://authserver.nju.edu.cn/authserver/login'
        res = self.session.post(url=login_url, data=form, allow_redirects=False)
        print(res.status_code, res.headers, res.cookies)
        # url = 'https://authserver.nju.edu.cn/authserver/login'
        # r = requests.post(url=url, data=form)
        # print(requests.session().cookies)
        

if __name__ == '__main__':
    a = authserve_login()
    a.login()
