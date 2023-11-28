# Breaker

## 动机
> 现在的消息来源很广，且更新频率高，更夹杂众多噪声干扰，可能经常会错过重要的消息，有没有一种办法可以及时获取自己需要的消息。
> <p style="text-align: right;">—— 1016-1022: Let's Begin</p>

当下南大学生学习的主要矛盾已经转变为日益增长的南大学生 ~~内卷~~ 自主学习需求与信息获取不及时不充分之间的矛盾。

相信大家已经发现，南大的各类教学活动信息分布十分分散 ~~很有江苏特色~~ ，在大多数情况下，我们都需要通过各种渠道获得最新发布的信息。如何快速获得信息，并进行存储、归类，方便我们个性化筛选？Python 为我们提供了一套很好的方法。

## 更新日志
### 2023.11.28
- 发布生产环境分支，删除无用代码

## 项目结构
- 主程序
  - breaker.py
- 数据库
  - 爬虫数据：database_sqlite.py
  - 用户数据：database_users.py
  - 数据存储：nova.db
- 爬虫
  - 通知网站：website.py
  - 五育系统：ndwy_login.py
    - 登录：authserver.py
  - 微信公众号：wechat.py
    - 登录信息：./data/wechat.pkl
- 数据筛选：search.py
- 邮件发送：send_email.py
  - 邮件模板：./html/
- 日志模块：log.py
  - 日志记录：
    - 主程序日志：./log/breaker.log
    - 微信公众号爬虫日志：./log/wechat.log