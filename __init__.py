#!/usr/bin/python3
# -*- coding: utf8 -*-
import configparser
import logging
import os
import re
import xml.etree.ElementTree as ET

from . import util
from flask import Flask, request
from flask.ext.mysql import MySQL

app = Flask(__name__)

# read config
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.dirname(os.path.realpath(__file__)) + "/config")

# initialize mysql
MYSQL = MySQL()
app.config['MYSQL_DATABASE_USER'] = CONFIG["Database"]["MYSQL_USER"]
app.config['MYSQL_DATABASE_PASSWORD'] = CONFIG["Database"]["MYSQL_PWD"]
app.config['MYSQL_DATABASE_DB'] = CONFIG["Database"]["MYSQL_DB"]
app.config['MYSQL_DATABASE_HOST'] = CONFIG["Database"]["MYSQL_HOST"]
MYSQL.init_app(app)
CONN = MYSQL.connect()

HELPER_INFO = \
"""您可以发送以下引号内消息进行操作：
“邮箱 email_address”，注册或更新您的邮箱
“推送 X”，打开邮件推送并设置周期为X天
“取消”，取消邮件推送
“来源”，查看可用的信息来源
“管理”，查看并管理订阅内容"""


def wechat_open_id_to_user_id(wechat_open_id):
    cursor = CONN.cursor()
    sql = "SELECT user_id FROM User WHERE wechat_open_id = %s"
    cursor.execute(sql, (wechat_open_id,))
    user = cursor.fetchall()
    if len(user) != 1:
        return None
    else:
        return user[0][0]


def site_id_to_site_name(site_id):
    cursor = CONN.cursor()
    sql = "SELECT site_name FROM Site WHERE site_id = %s"
    cursor.execute(sql, (site_id,))
    site = cursor.fetchall()
    if len(site) != 1:
        return None
    else:
        return site[0][0]


def save_message(wechat_open_id, message, inbound=True):
    cursor = CONN.cursor()
    cursor.execute("INSERT INTO WeChatMessage (wechat_open_id, message, inbound) VALUES (%s, %s, %s)",
                   (wechat_open_id, message, inbound))
    CONN.commit()


def set_email(wechat_open_id, email):
    cursor = CONN.cursor()
    sql = "SELECT COUNT(*) FROM User WHERE wechat_open_id = %s"
    cursor.execute(sql, (wechat_open_id,))

    if cursor.fetchone()[0] == 0:  # create user
        sql = "INSERT INTO User (wechat_open_id, email) VALUES (%s, %s)"
        cursor.execute(sql, (wechat_open_id, email))
        CONN.commit()
        return "注册邮箱{}成功！\n\n默认推送周期为7天，发送 “推送 X” 更新为X天。您可以发送 “来源” 查看并订阅信息。".format(email)
    else:  # update user
        sql = "UPDATE User SET email = %s WHERE wechat_open_id = %s"
        cursor.execute(sql, (email, wechat_open_id))
        CONN.commit()
        return "更新邮箱为{}！".format(email)


def set_interval(wechat_open_id, interval):
    cursor = CONN.cursor()
    sql = "SELECT COUNT(*) FROM User WHERE wechat_open_id = %s"
    cursor.execute(sql, (wechat_open_id,))

    if cursor.fetchone()[0] == 0:  # not register email yet
        return "您尚未注册邮箱，发送 “邮箱 email_address” 进行注册！"
    else:  # update user
        sql = "UPDATE User SET activated = TRUE, sending_interval = %s WHERE wechat_open_id = %s"
        cursor.execute(sql, (interval, wechat_open_id))
        CONN.commit()
        return "更新推送周期为{}天！".format(interval)


def deactivate_user(wechat_open_id):
    cursor = CONN.cursor()
    sql = "SELECT COUNT(*) FROM User WHERE wechat_open_id = %s"
    cursor.execute(sql, (wechat_open_id,))

    if cursor.fetchone()[0] == 0:  # not register email yet
        return "您尚未注册邮箱，发送 “邮箱 email_address” 进行注册！"
    else:  # update user
        sql = "UPDATE User SET activated = FALSE WHERE wechat_open_id = %s"
        cursor.execute(sql, (wechat_open_id,))
        CONN.commit()
        return "取消推送成功。您可以发送 “推送 X” 再次打开X天为周期的邮件推送。"


def get_catalog():
    cursor = CONN.cursor()
    sql = "SELECT school_name, school_id FROM School"
    cursor.execute(sql)

    reply = "SJTU Noticer目前提供以下信息分类：\n\n"
    for entry in cursor.fetchall():
        name, school_id = entry
        reply += " - {}，{}\n".format(name, school_id)
    reply += "\n发送 “详情 X” 查看具体项目，X为类别后的编号"
    return reply


def get_sites(school_id):
    cursor = CONN.cursor()

    # check if school_id is valid
    sql = "SELECT school_name FROM School WHERE school_id = %s"
    cursor.execute(sql, (school_id,))
    school = cursor.fetchall()
    if len(school) != 1:
        return "请输入正确的编号。您可以发送 “来源” 查看所有信息来源。"
    school_name = school[0][0]

    # get all the sites
    sql = "SELECT site_name, site_id FROM Site WHERE school_id = %s"
    cursor.execute(sql, (school_id,))

    reply = "{}目前提供以下项目：\n\n".format(school_name)
    for entry in cursor.fetchall():
        name, site_id = entry
        reply += " - {}，{}\n".format(name, site_id)
    reply += "\n发送 “订阅 X” 订阅具体项目，X为项目后的编号"
    return reply


def subscribe(wechat_open_id, site_id):
    cursor = CONN.cursor()

    # check site id
    site_name = site_id_to_site_name(site_id)
    if site_name is None:
        return "请输入正确的编号。您可以发送 “来源” 查看所有信息来源。"

    # get user_id
    user_id = wechat_open_id_to_user_id(wechat_open_id)
    if user_id is None:
        return "您尚未注册邮箱，请发送 “邮箱 email_address” 注册邮箱。"

    # subscribe
    sql = "SELECT COUNT(*) FROM Subscription WHERE user_id = %s AND site_id = %s"
    cursor.execute(sql, (user_id, site_id))
    if cursor.fetchone()[0] == 1:  # avoid duplicate
        return "您已成功订阅{}".format(site_name)
    sql = "INSERT INTO Subscription (user_id, site_id) VALUES (%s, %s)"
    cursor.execute(sql, (user_id, site_id))
    CONN.commit()
    return "您已成功订阅{}".format(site_name)


def get_subscription(wechat_open_id):
    # get user_id
    user_id = wechat_open_id_to_user_id(wechat_open_id)
    if user_id is None:
        return "您尚未注册邮箱，请发送 “邮箱 email_address” 注册邮箱。"

    cursor = CONN.cursor()
    sql = "SELECT sending_interval, activated FROM User WHERE wechat_open_id = %s"
    cursor.execute(sql, (wechat_open_id,))
    interval, activated = cursor.fetchone()
    if activated:
        reply = "您的推送周期为{}天，目前订阅了：\n\n".format(interval)

        sql = """SELECT school_name, site_name, site_id
                 FROM Subscription JOIN Site USING (site_id) JOIN School USING (school_id)
                 WHERE user_id = %s
                 ORDER BY school_name ASC"""
        cursor.execute(sql, (user_id,))
        result = {}
        for entry in cursor.fetchall():
            school_name, site_name, site_id = entry
            if school_name not in result:
                result[school_name] = [(site_name, site_id)]
            else:
                result[school_name].append((site_name, site_id))


        for item in result.items():
            reply += item[0] + "\n"
            for site in item[1]:
                reply += " - {}，{}\n".format(site[0], site[1])
        reply += "\n发送 “取消” 取消邮件推送，发送 “推送 X” 更新推送周期为X天，发送 “取消 X” 取消编号为X的项目，发送 “来源” 查看更多消息来源。"
    else:
        reply = "您已取消邮件推送，发送 “推送 X” 再次打开X天为周期的邮件推送，发送 “来源” 查看更多消息来源。"

    return reply


def cancel_subscription(wechat_open_id, site_id):
    # get user_id
    user_id = wechat_open_id_to_user_id(wechat_open_id)
    if user_id is None:
        return "您尚未注册邮箱，请发送 “邮箱 email_address” 注册邮箱。"

    cursor = CONN.cursor()
    sql = "SELECT COUNT(*) FROM Subscription WHERE user_id = %s AND site_id = %s"
    cursor.execute(sql, (user_id, site_id))
    if cursor.fetchone()[0] == 0:
        return "您尚未订阅该项目。"

    sql = "DELETE FROM Subscription WHERE user_id = %s AND site_id = %s"
    cursor.execute(sql, (user_id, site_id))
    CONN.commit()
    return "取消成功！"


def log_message(dealer):
    def wrapper_dealer(*args, **kwargs):
        save_message(args[0], args[1], inbound=True)
        reply = dealer(*args, **kwargs)
        save_message(args[0], reply, inbound=False)
        return reply
    return wrapper_dealer


@log_message
def deal_message(wechat_open_id, message):
    if message.startswith("邮箱"):
        if len(message.split()) == 2:
            _, email = message.split()
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return "请使用合法的邮箱地址。"
            return set_email(wechat_open_id, email)
        else:
            return "请按照 “邮件 email_address” 格式发送信息。"
    elif message.startswith("推送"):
        try:
            _, interval = message.split()
            interval = int(interval)
            if interval <= 0:
                return "请使用正数周期。"
            return set_interval(wechat_open_id, interval)
        except ValueError:
            return "请按照 “推送 X” 格式发送信息，X为推送周期（天）。"
    elif message.startswith("取消"):
        if message == "取消":
            return deactivate_user(wechat_open_id)

        try:
            _, site_id = message.split()
            site_id = int(site_id)
            return cancel_subscription(wechat_open_id, site_id)
        except ValueError:
            return "请按照 “取消 X” 格式发送信息，X为项目编号。"
    elif message.startswith("来源"):
        return get_catalog()
    elif message.startswith("详情"):
        try:
            _, school_id = message.split()
            school_id = int(school_id)
            return get_sites(school_id)
        except ValueError:
            return "请按照 “详情 X” 格式发送信息，X为项目编号。您可以发送 “来源” 查看可用的消息来源。"
    elif message.startswith("订阅"):
        try:
            _, site_id = message.split()
            site_id = int(site_id)
            return subscribe(wechat_open_id, site_id)
        except ValueError:
            return "请按照 “订阅 X” 格式发送信息，X项目编号。您可以发送 “来源” 查看可用的消息来源。"
    elif message.startswith("管理"):
        return get_subscription(wechat_open_id)
    else:
        return HELPER_INFO


@app.route("/", methods=["GET"])
def hello_world():
    echostr = request.args.get("echostr", "")
    return echostr if util.is_from_wechat(request) else "这不是微信请求呢"


@app.route("/", methods=["POST"])
def receive_text():
    if not util.is_from_wechat(request):
        return "这不是微信请求呢"

    # get common data
    xmldata = ET.fromstring(request.data.decode("utf8"))
    from_user_name = xmldata.find("FromUserName").text
    to_user_name = xmldata.find("ToUserName").text
    create_time = xmldata.find("CreateTime").text
    msg_type = xmldata.find("MsgType").text

    if msg_type == "text":
        content = xmldata.find("Content").text
        msg_id = xmldata.find("MsgId").text

        reply = deal_message(from_user_name, content)
        return util.text_reply(to_user=from_user_name, from_user=to_user_name, content=reply)
    else:
        return util.default_reply(to_user=from_user_name, from_user=to_user_name)


if __name__ == "__main__":
    app.run()
