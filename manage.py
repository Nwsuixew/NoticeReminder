# Python Standard Library
import argparse
import configparser
import logging
# Third Party Library
from apscheduler.schedulers.blocking import BlockingScheduler
# User Library
import db
import myemail
import process


def main():
    """
    检测是否有新通知
    检测到新通知后，从数据库拉取用户，根据部门订阅情况发送提醒邮件
    :return:
    """
    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')
    department_table_names = config['Database']['DepartmentTableNames'].split(',')
    departments = config['Database']['Departments'].split(',')
    n = len(department_table_names)

    new_notice = process.all_page_update_detect()   # 获取每个部门的新通知

    updated = [0] * n    # 为每个部门设置一个“检测到新通知”的标志位

    for i in range(n):
        if new_notice[i]:   # 遍历列表new_notice，若表中某一元组不为空，则对应部门网站有了新通知，“检测到新通知”标志位置1
            updated[i] = 1

    if sum(updated) > 0:    # “检测到新通知”标志位之和大于0 -> 检测到新通知
        user_list = db.fetch_row_all(config['Database']['UserDatebaseName'], config['Database']['UserTableName'],
                                     ', '.join(department_table_names) + ', email')   # 拉取全部用户(没考虑用户表很大的情况)

        for user in user_list:
            content = ''
            for i in range(n):
                if user[i] and updated[i]:  # 用户订阅了且该网站的通知也更新了，就将新通知添加到邮件正文
                    content += myemail.generate_content(departments[i], new_notice[i])
            if content:
                res = myemail.send('nwsuixew@qq.com', user[n], 'Nwsuixew通知提醒服务', content)  # 发出邮件
                print(res)


def manage():
    logging.basicConfig(filename='NoticeReminder.log', format='[%(asctime)s] [%(levelname)s]: [%(message)s]',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    parser = argparse.ArgumentParser(description='Manage')
    parser.add_argument('-init', action='store_true', default=False, help='init NoticeReminder')
    parser.add_argument('-run', action='store_true', default=False, help='run NoticeReminder')

    args = parser.parse_args()
    if args.init:
        process.init()
    elif args.run:
        scheduler = BlockingScheduler()
        scheduler.add_job(main, "cron", hour="8-22", minute="*/10")     # 8:00-23:00，每10分钟检测一次通知更新
        print('PROGRAM START')
        scheduler.start()


manage()
