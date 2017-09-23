#!/usr/bin/python3
# -*- coding: utf8 -*-
import logging
import xml.etree.ElementTree as ET

from . import util
from flask import Flask, request


app = Flask(__name__)


def save_message(wechat_open_id, message):
    # todo
    pass


def deal_message(wechat_open_id, message):
    save_message(wechat_open_id, message)

    return "你的微信OpenID是：「{}」\n\n刚发送了：「{}」".format(wechat_open_id, message)


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
