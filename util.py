#!/usr/bin/python3
# -*- coding: utf8 -*-

import hashlib
from time import time


TOKEN = "LongAsHeLives"
DEFAULT_PROMPT = \
"""欢迎使用SJTU Noticer校园信息订阅服务！通过SJTU Noticer，您可以自主选择订阅内容（X院学生办、Y院团委等）。我们将为您通过邮件，定期推送最新校园通知。

您可以发送以下消息进行操作：
<邮箱 email_address>，注册或更新您的邮箱
<推送 X>，打开邮件推送并设置周期为X天
<取消>，取消邮件推送
<来源>，查看可用的信息来源
<管理>，查看并管理订阅内容

您也可以通过留言进行反馈，帮助我们做得更好！"""


def is_from_wechat(request):
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")

    args = [TOKEN, timestamp, nonce]
    args.sort()
    sha1 = hashlib.sha1()
    sha1.update("".join(args).encode('utf-8'))
    hashcode = sha1.hexdigest()

    if hashcode == signature:
        return True
    else:
        return False


def text_reply(to_user, from_user, content):
    template = "<xml><ToUserName><![CDATA[{to_user}]]></ToUserName><FromUserName><![CDATA[{from_user}]]></FromUserName><CreateTime>{create_time}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{content}]]></Content></xml>"
    return template.format(to_user=to_user, from_user=from_user, create_time=int(time()), content=content)


def default_reply(to_user, from_user):
    template = "<xml><ToUserName><![CDATA[{to_user}]]></ToUserName><FromUserName><![CDATA[{from_user}]]></FromUserName><CreateTime>{create_time}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{content}]]></Content></xml>"
    return template.format(to_user=to_user, from_user=from_user, create_time=int(time()), content=DEFAULT_PROMPT)
