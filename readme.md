# NoticeReminder

**一份用于杭电校内的通知提醒脚本**  
**脚本启动后8:00 - 23:00每10分钟爬取一遍目标网页**  
**检测到新通知后，邮件提醒数据库中订阅了该网站的用户**

## 目前支持的页面：

- 教务处-通知公告
- 通信工程学院-本科教育
- 计算机学院-本科教育
- 计算机学院-研究生教育

## 使用前安装：

- Python 3.8
- Python第三方库：apscheduler、bs4
- SQLite

## 启动前配置

- 用于发送邮件的邮箱账号及密码，详见 >NoticeReminder.ini<

## 使用教程

- 脚本初始化  
根据ini文件进行数据库相关的初始化，后期更改脚本后也需要再次初始化以在数据库中应用更改

```
python3.8 manage.py -init
```

- 向数据库添加用户

```
python3.8 usermanage.py -a (学号) (邮箱) (订阅) ...

示例：
当前用户表格式：sid | email | jwc | comm
添加用户a，学号12345678，邮箱user@qq.com，订阅教务处通知，不订阅通信工程学院通知
python3.8 usermanage.py -a 12345678 user@qq.com 1 0
```

- 查看用户表格式

```
python3.8 usermanage.py -f

输出示例：
SID       Email               jwc comm
```

- 更新用户信息

```
python3.8 usermanage.py -u (学号) (邮箱 | 网站) (新邮箱 | 订阅)

示例：
更改邮箱：python3.8 usermanage.py -u 12345678 newuser@qq.com
更改订阅：python3.8 usermanage.py -u 12345678 jwc 0
```

- 查看所有用户信息

```
python3.8 usermanage.py -l

示例：
SID       Email               jwc comm
12345678  newuser@qq.com      0 0
```