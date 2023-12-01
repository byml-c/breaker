import time
import pytz
import logging
import datetime

class logger:
    path = './log/{}.log'
    format = '%(asctime)s [%(levelname)s]: %(message)s'

    def __init__(self, name:str):
        '''
            初始化日志

            name: 日志名，保存成的文件会在 ./log/<name>.log 下
                通过 path 可以改变保存位置
            
            默认在控制台输出所有级别的日志，
            在文件中只写入 INFO 及以上级别的日志
        '''

        self.logger = logging.getLogger(name)
        # 默认不向父记录器传递日志信息
        self.logger.propagate = False
        self.format = logging.Formatter(self.format)

        # 获取 UTC+8 时区
        utc_8 = pytz.timezone('Asia/Shanghai')
        # 时间设置为 UTC+8 时区
        self.format.converter = lambda *args: datetime.datetime.now(utc_8).timetuple()

        self.console = logging.StreamHandler()
        self.console.setLevel(logging.INFO)
        self.console.setFormatter(self.format)
        self.logger.addHandler(self.console)

        self.file = logging.FileHandler(
              filename=self.path.format(name),mode='a',encoding='utf-8')
        self.file.setLevel(logging.INFO)
        self.file.setFormatter(self.format)
        self.logger.addHandler(self.file)

        self.logger.setLevel(logging.INFO)
    
    def __del__(self):
        '''
            析构函数，清空记录器绑定，避免重复输出
        '''
        
        self.logger.handlers.clear()

    def write(self, content:str, type:str='D'):
        '''
            写入日志

            type: 消息类型
                D: debug, I: info, W: warning, E: error
            content: 写入内容
        '''
        
        # print(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime()), type, content)
        if type == 'D':
            self.logger.debug(content)
        elif type == 'I':
            self.logger.info(content)
        elif type == 'W':
            self.logger.warning(content)
        elif type == 'E':
            self.logger.error(content)

if __name__ == '__main__':
    a = logger('log')
    a.write('Hello')
    a.write('World!', 'I')