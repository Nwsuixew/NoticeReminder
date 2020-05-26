# Python Standard Library
import configparser
import logging
import smtplib
from email.mime.text import MIMEText


def generate_content(department: str, new_notice: list):
    """
    生成邮件正文
    :param department: 网页部门
    :param new_notice: 新通知
    :return:
    """
    content = department + ':\n'
    for notice in new_notice:
        content += ' ' * 4 + notice[0] + ' ' * 4 + notice[1] + '\n'
    return content + '\n'


def send(sender: str, receiver: str, title: str, content: str):
    """
    发送邮件
    :param sender: 发件人
    :param receiver: 收件人
    :param title: 邮件标题
    :param content: 邮件正文
    :return: 发送结果
    """
    config = configparser.ConfigParser()
    config.read('NoticeReminder.ini', 'utf-8')

    message = MIMEText(content)
    message['Subject'] = title
    message['From'] = sender
    message['To'] = receiver

    try:
        smtp_obj = smtplib.SMTP_SSL(config['Email']['host'], int(config['Email']['port']))
        smtp_obj.login(config['Email']['account'], config['Email']['password'])
        smtp_obj.sendmail(sender, receiver, message.as_string())
        smtp_obj.quit()
        logging.info('EMAIL HAS BEEN SENT: <%s>', receiver)
        return 'EMAIL HAS BEEN SENT: <%s>' % receiver
    except smtplib.SMTPException as e:
        logging.warning(str(e))
        return str(e)
