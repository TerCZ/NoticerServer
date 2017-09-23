#!/usr/bin/python3
# -*- coding: utf8 -*-
import configparser
import logging
import os
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


def save_message(wechat_open_id, message):
    cursor = CONN.cursor()
    cursor.execute("INSERT INTO WeChatMessage (wechat_open_id, message) VALUES (%s, %s)", (wechat_open_id, message))
    CONN.commit()


def deactivate_user(wechat_open_id):
    cursor = CONN.cursor()
    sql = "SELECT COUNT(*) FROM USER WHERE wechat_open_id = %s"
    cursor.execute(sql, (wechat_open_id,))

    if cursor.fetchone()[0] == 0:  # not register email yet
        return "您尚未注册邮箱，发送「邮箱 email_address」进行注册！"
    else:  # update user
        sql = "UPDATE User SET activated = FALSE WHERE wechat_open_id = %s"
        cursor.execute(sql, (wechat_open_id,))
        CONN.commit()
        return "取消推送成功！"


def set_interval(wechat_open_id, interval):
    cursor = CONN.cursor()
    sql = "SELECT COUNT(*) FROM USER WHERE wechat_open_id = %s"
    cursor.execute(sql, (wechat_open_id,))

    if cursor.fetchone()[0] == 0:  # not register email yet
        return "您尚未注册邮箱，发送「邮箱 email_address」进行注册！"
    else:  # update user
        sql = "UPDATE User SET sending_interval = %s WHERE wechat_open_id = %s"
        cursor.execute(sql, (interval, wechat_open_id))
        CONN.commit()
        return "更新推送周期为{}天！".format(interval)


def get_catalog():
    cursor = CONN.cursor()
    sql = "SELECT school_name, school_id FROM School"
    cursor.execute(sql)

    reply = "SJTU Noticer目前提供以下信息分类：\n"
    for entry in cursor.fetchall():
        name, school_id = entry
        reply += "\t{}，{}\n".format(name, school_id)
    reply += "\n发送「详情 X」查看该类别提供的具体项目，X为类别后面的数字"
    return reply


def set_email(wechat_open_id, email):
    cursor = CONN.cursor()
    sql = "SELECT COUNT(*) FROM USER WHERE wechat_open_id = %s"
    cursor.execute(sql, (wechat_open_id,))

    if cursor.fetchone()[0] == 0:  # create user
        sql = "INSERT INTO User (wechat_open_id, email) VALUES (%s, %s)"
        cursor.execute(sql, (wechat_open_id, email))
        CONN.commit()
        return = "注册邮箱{}成功！\n默认推送周期为7天，您可通过发送「订阅 X」更新为X天。\n您可通过发送「信息来源」查看并订阅校园信息。".format(email)
    else:  # update user
        sql = "UPDATE User SET email = %s WHERE wechat_open_id = %s"
        cursor.execute(sql, (email, wechat_open_id))
        CONN.commit()
        return "更新邮箱为{}！".format(email)


def deal_message(wechat_open_id, message):
    save_message(wechat_open_id, message)

    if message.startswith("取消"):
        return deactivate_user(wechat_open_id)
    elif message.startswith("订阅"):
        try:
            _, interval = message.split()
            return set_interval(wechat_open_id=, int(interval))
        except Exception as e:
            return "请按照「订阅 X」格式发送信息，X为推送周期（天）。"
    elif message.startswith("信息来源"):
        return get_catalog()
    elif message.startswith("邮箱"):
        try:
            _, email = message.split()
            return set_email(email)
        except Exception as e:
            return "请按照「订阅 email_address」格式发送信息。"
    elif message.startswith("详情"):
        return "功能尚未实现呢"
    else:
        return "你的微信OpenID是：「{}」\n刚发送了：「{}」\n这是不支持的文本哦".format(wechat_open_id, message)


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
