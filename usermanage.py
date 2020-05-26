# Python Standard Library
import argparse
import configparser
import logging
import re
# User Library
import db


def init():
    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')
    db_name = config['Database']['DatabaseName']
    user_table_name = config['Database']['UserTableName']

    db.create_db(db_name)
    if not db.is_table_exist(db_name, user_table_name):
        db.create_table(db_name, user_table_name, 'sid text, email text')

    for name in config['Database']['DepartmentTableNames'].split(','):
        if not db.is_column_exist(db_name, user_table_name, name):
            db.insert_column(db_name, user_table_name, name + ' int')


def get_all_user():
    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')

    return db.fetch_row_all(config['Database']['DatabaseName'], config['Database']['UserTableName'],
                            ', '.join(config['Database']['DepartmentTableNames'].split(',')) + ', email')


def is_sid_correct(sid: str):
    """
    检查学号是否正确（格式检查）
    :param sid: 学号字符串
    :return:
    """
    if (len(sid) != 8 and len(sid) != 9) \
            or (len(sid) == 8 and re.search(r'\d{8}', sid) is None) \
            or (len(sid) == 9 and re.search(r'\d{9}', sid) is None):
        return False
    else:
        return True


def add_user(args: list):
    """
    添加用户
    :param args: [学号，邮箱，订阅，[订阅]]
    :return: None
    """
    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')
    department_table_names = config['Database']['DepartmentTableNames'].split(',')
    n = len(department_table_names)

    if len(args) != 2 + n:  # 2 means sid and email, n means number of department
        print('Missing arguments or too many arguments')
        return

    if not is_sid_correct(args[0]):
        print('SID incorrect, only can be 8-9 digits pure number')
        return

    if re.search(r'[0-9a-zA-Z_\-.]+@[0-9a-zA-Z]+\.[0-9a-zA-Z.]', args[1]) is None:  # 检查邮箱格式
        print('Email incorrect')
        return

    for arg in args[2:]:
        if not arg.isdigit():
            print('Subscription argument incorrect, only can be 0 or 1')
            return

    db.insert_row(config['Database']['DatabaseName'], config['Database']['UserTableName'],
                  'sid, email, ' + ', '.join(department_table_names),
                  "'%s', '%s', " % (args[0], args[1]) + ', '.join(args[2:]))

    log_info = 'ADD USER: <%s> <%s> <' % (args[0], args[1]) + '> <'.join(args[2:]) + '>'
    logging.info(log_info)
    print(log_info)


def update_user(args: list):
    """
    更新用户信息
    :param args: [学号，邮箱|订阅，参数]
    :return: None
    """
    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')

    if len(args) != 3:
        print('Missing arguments or too many arguments')
        return

    if not is_sid_correct(args[0]):
        print('SID incorrect, only can be 8-9 digits pure number')
        return

    if args[1] not in ['email'] + config['Database']['DepartmentTableNames'].split(','):
        print('Argument incorrect')
        return
    else:
        if args[1] == 'email' and re.search(r'[0-9a-zA-Z_\-.]+@[0-9a-zA-Z]+\.[0-9a-zA-Z.]', args[1]) is None:
            print('Email incorrect')
            return

        if not args[2].isdigit():
            print('Subscription argument incorrect, only can be 0 or 1')
            return

    db.update_row(config['Database']['DatabaseName'], config['Database']['UserTableName'],
                  '%s = %s' % (args[1], args[2]), 'sid = %s' % args[0])
    logging.info('UPDATE USER: <%s> <%s> <%s>', args[0], args[1], args[2])
    print('UPDATE USER: <%s> <%s> <%s>' % (args[0], args[1], args[2]))


def show_user():
    """
    打印用户列表
    :return: None
    """
    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')

    user_list = db.fetch_row_all(config['Database']['DatabaseName'], config['Database']['UserTableName'], '*')

    print('SID       Email                    ' + ' '.join(config['Database']['DepartmentTableNames'].split(',')))
    for user in user_list:
        print('%-10s%-25s' % (user[1], user[2]) + ' '.join([str(n) for n in user[3:]]))


def show_table_format():
    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')
    print('SID       Email                    ' + ' '.join(config['Database']['DepartmentTableNames'].split(',')))


def user_manage():
    logging.basicConfig(filename='NoticeReminder.log', format='[%(asctime)s] [%(levelname)s]: [%(message)s]',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
    parser = argparse.ArgumentParser(description='User Manage')
    parser.add_argument('-a', action='extend', nargs="+", type=str, help='add user info')
    parser.add_argument('-u', action='extend', nargs="+", type=str, help='update user info')
    parser.add_argument('-l', action='store_true', default=False, help='show user info')
    parser.add_argument('-f', action='store_true', default=False, help='show table format')

    args = parser.parse_args()
    if args.a:
        add_user(args.a)

    elif args.u:
        update_user(args.u)

    elif args.l:
        show_user()

    elif args.f:
        show_table_format()


user_manage()
