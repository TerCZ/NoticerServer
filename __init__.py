#!/usr/bin/python3
# -*- coding: <encoding name> -*-
import logging

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

    message = request.data.decode("utf8")
    logging.debug(message)

    # to_user_name = request.form.get("ToUserName")
    # from_user_name = request.form.get("FromUserName")
    # create_time = request.form.get("CreateTime")
    # msg_type = request.form.get("MsgType")
    # if msg_type == "text":
    #     content = request.form.get("Content")
    #     msg_id = request.form.get("MsgId")
    #
    #     app.logger.debug("ToUserName: {}\tFromUserName: {}\tCreateTime: {}\tMsgType: {}\tContent: {}\tMsgId: {}\t".format(
    #         to_user_name, from_user_name, create_time, content, msg_id))

    return "success"


if __name__ == "__main__":
    app.run()
