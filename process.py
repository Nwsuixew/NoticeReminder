# Python Standard Library
import configparser
import logging
import re
from datetime import date
from urllib import error, request
# Third Party Library
from bs4 import BeautifulSoup
# User Library
import db


def request_page(url: str, encoding='UTF-8'):
    """
    请求网页的html
    :param url: 网页链接
    :param encoding: 网页编码方式，默认utf-8
    :return: html
    """
    header = {
        'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
            'q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ko;q=0.7,ja;q=0.6,zh-TW;q=0.5,und;q=0.4',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        # 'Cookie': '',
        # 'Host': '',
        # 'Referer': '',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/81.0.4044.129 Safari/537.36'
    }
    req = request.Request(url, None, header)

    try:
        response = request.urlopen(req)
        return response.read().decode(encoding)
    except (error.HTTPError, error.URLError, error.ContentTooShortError) as e:
        return str(e)


def get_local_notice_record(table: str, length: int):
    """
    从数据库拉取旧通知
    :param table: 表名
    :param length: 拉取的通知数
    :return: 通知（元组形式（标题，链接，发布日期））
    """
    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')

    res = db.fetch_row_descending(config['Database']['DatabaseName'], table, 'title, url, date', length=length)

    return tuple(res)


def store_notice_locally(table: str, title, url, publish_date):
    """
    保存通知
    :param table: 表名
    :param title: 通知标题
    :param url: 通知链接
    :param publish_date: 发布日期
    :return: None
    """
    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')

    db.insert_row(config['Database']['DatabaseName'], table,
                  'title, url, date', "'%s', '%s', '%s'" % (title, url, publish_date))


def all_page_update_detect():
    new_notice = list()

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[Customize Part 1/5]<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    new_notice.append(page_update_detect_jwc())
    new_notice.append(page_update_detect_comm())
    new_notice.append(page_update_detect_cs_bk())
    new_notice.append(page_update_detect_cs_yjs())
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    return tuple(new_notice)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[Customize Part 2/5]<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def page_parse_jwc() -> tuple:
    """
    解析教务处通知页面
    通过BeautifulSoup实现html解析
    :return: 解析到的通知（元组）
    """
    soup = BeautifulSoup(request_page('http://jwc.hdu.edu.cn/tzgg/list.htm'), 'html.parser')
    tags = soup.find_all(class_=re.compile(r'news-list n\d+ clearfix'))

    res = []
    for tag in tags:
        res.append((tag.a['title'], 'http://jwc.hdu.edu.cn' + tag.a['href'], tag.div.string))

    return tuple(res)


def page_parse_comm() -> tuple:
    """
    解析通信工程学院本科教育页面
    :return: 解析到的通知（元组）
    """
    soup = BeautifulSoup(request_page('http://comm.hdu.edu.cn/bkjy/list.htm'), 'html.parser')
    tags = soup.find_all(class_=re.compile(r'list_item i\d+'))

    res = []
    for tag in tags:
        res.append((tag.a['title'], 'http://comm.hdu.edu.cn' + tag.a['href'],
                    tag.find(class_='Article_PublishDate').string))

    return tuple(res)


def page_parse_cs_bk() -> tuple:
    """
    解析计算机学院本科教育页面
    通过BeautifulSoup实现html解析
    :return: 解析到的通知（元组）
    """
    soup = BeautifulSoup(request_page('http://computer.hdu.edu.cn/1309/list.htm'), 'html.parser')
    tags = soup.find(class_='news_list').find_all(name='li')

    res = []
    for tag in tags:
        res.append((tag.a.string, 'http://computer.hdu.edu.cn' + tag.a['href'], tag.span.string))

    return tuple(res)


def page_parse_cs_yjs() -> tuple:
    """
    解析计算机学院研究生教育页面
    通过BeautifulSoup实现html解析
    :return: 解析到的通知（元组）
    """
    soup = BeautifulSoup(request_page('http://computer.hdu.edu.cn/1310/list.htm'), 'html.parser')
    tags = soup.find(class_='news_list').find_all(name='li')

    res = []
    for tag in tags:
        res.append((tag.a.string, 'http://computer.hdu.edu.cn' + tag.a['href'], tag.span.string))

    return tuple(res)
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[Customize Part 3/5]<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def page_update_detect_jwc():
    """
    检测是否有新通知
    :return: 新通知
    """
    local_notice = get_local_notice_record('jwc', 15)
    current_notice = page_parse_jwc()
    new_notice = []

    for notice in current_notice:
        # 先判断发布日期是否是当天，再判断通知是否在本地记录中，以判断是否是新通知
        if date.fromisoformat(notice[2]) == date.today() and notice not in local_notice:
            new_notice.append(notice)
            store_notice_locally('jwc', notice[0], notice[1], notice[2])    # 判断是新通知，添加到本地记录中
            logging.info('NEW NOTICE: <jwc> <%s> <%s>', notice[0], notice[1])
            print('NEW NOTICE: <jwc> <%s> <%s>' % (notice[0], notice[1]))

    return tuple(new_notice)


def page_update_detect_comm():
    local_notice = get_local_notice_record('comm', 14)
    current_notice = page_parse_comm()
    new_notice = []

    for notice in current_notice:
        if date.fromisoformat(notice[2]) == date.today() and notice not in local_notice:
            new_notice.append(notice)
            store_notice_locally('comm', notice[0], notice[1], notice[2])
            logging.info('NEW NOTICE: <comm> <%s> <%s>', notice[0], notice[1])
            print('NEW NOTICE: <comm> <%s> <%s>' % (notice[0], notice[1]))

    return tuple(new_notice)


def page_update_detect_cs_bk():
    local_notice = get_local_notice_record('cs_bk', 20)
    current_notice = page_parse_cs_bk()
    new_notice = []

    for notice in current_notice:
        if date.fromisoformat(notice[2]) == date.today() and notice not in local_notice:
            new_notice.append(notice)
            store_notice_locally('cs_bk', notice[0], notice[1], notice[2])
            logging.info('NEW NOTICE: <cs_bk> <%s> <%s>', notice[0], notice[1])
            print('NEW NOTICE: <cs_bk> <%s> <%s>' % (notice[0], notice[1]))

    return tuple(new_notice)


def page_update_detect_cs_yjs():
    local_notice = get_local_notice_record('cs_yjs', 20)
    current_notice = page_parse_cs_yjs()
    new_notice = []

    for notice in current_notice:
        if date.fromisoformat(notice[2]) == date.today() and notice not in local_notice:
            new_notice.append(notice)
            store_notice_locally('cs_yjs', notice[0], notice[1], notice[2])
            logging.info('NEW NOTICE: <cs_yjs> <%s> <%s>', notice[0], notice[1])
            print('NEW NOTICE: <cs_yjs> <%s> <%s>' % (notice[0], notice[1]))

    return tuple(new_notice)
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>[Customize Part 4/5]<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
functions = [
    page_parse_jwc(),
    page_parse_comm(),
    page_parse_cs_bk(),
    page_parse_cs_yjs()
]
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


def init():
    """
    创建脚本所需数据库、表单，并填充数据
    :return: None
    """
    global functions

    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')
    db_name = config['Database']['DatabaseName']
    user_table_name = config['Database']['UserTableName']
    department_table_names = config['Database']['DepartmentTableNames'].split(',')

    logging.info('BEGIN INIT')
    print('BEGIN INIT')

    db.create_db(db_name)  # 创建数据库
    if not db.is_table_exist(db_name, user_table_name):     # 用户表单不存在则创建用户表单
        db.create_table(db_name, user_table_name, 'sid text, email text')

    for i in range(len(department_table_names)):     # 遍历部门名称
        if not db.is_table_exist(db_name, department_table_names[i]):    # 对应的部门表单不存在则创建部门表单
            db.create_table(db_name, department_table_names[i], 'title text, url text, date text')

        if not db.is_column_exist(db_name, user_table_name, department_table_names[i]):  # 对应的部门列在用户表单里不存在则插入新列
            db.insert_column(db_name, user_table_name, department_table_names[i] + ' int')

        if not db.fetch_row_all(db_name, department_table_names[i], '*') and i < len(functions):   # 部门表单为空则进行预填充
            new_notice = functions[i]  # 预存当前网站上的通知，用于下次检测新通知时拿来对比
            for notice in new_notice[::-1]:  # 网站上的通知都是从上往下从新到旧，所以要倒序存放
                store_notice_locally(department_table_names[i], notice[0], notice[1], notice[2])

    logging.info('FINISH INIT')
    print('FINISH INIT')
