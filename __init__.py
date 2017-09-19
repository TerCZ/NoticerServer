#!/usr/bin/python3
# -*- coding: <encoding name> -*-
import logging
import xml.etree.ElementTree as ET

from flask import Flask, request
from .util import is_from_wechat

app = Flask(__name__)


@app.route("/", methods=["GET"])
def hello_world():
    echostr = request.args.get("echostr", "")
    return echostr if is_from_wechat(request) else "这不是微信请求呢"


@app.route("/", methods=["POST"])
def receive_text():
    if not is_from_wechat(request):
        return "这不是微信请求呢"

    # get common data
    message = request.data.decode("ascii")
    xmldata = ET.fromstring(message)
    from_user_name = xmldata.find("FromUserName").text
    to_user_name = xmldata.find("ToUserName").text
    create_time = xmldata.find("CreateTime").text
    msg_type = xmldata.find("MsgType").text

    logging.debug("ToUserName: {}\nFromUserName: {}\nCreateTime: {}\nMsgType: {}\n".format(to_user_name, from_user_name, create_time))


    if msg_type == "text":
        content = xmldata.find("Content").text
        msg_id = xmldata.find("MsgId").text

        logging.debug("Content: {}\nMsgId: {}\n".format(to_user_name, from_user_name, create_time, content, msg_id))


    return "success"


if __name__ == "__main__":
    app.run()
