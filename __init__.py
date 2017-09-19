#!/usr/bin/python3
# -*- coding: <encoding name> -*-
import logging
import util


from flask import Flask, request
# from util import is_from_wechat

app = Flask(__name__)


@app.route("/", methods=["GET"])
def hello_world():
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")

    echostr = request.args.get("echostr", "")

    if util.is_from_wechat(signature=signature, timestamp=timestamp, nonce=nonce):
        return echostr
    else:
        return "这不是微信请求呢"


@app.route("/", methods=["POST"])
def receive_text():
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")

    if not is_from_wechat(signature=signature, timestamp=timestamp, nonce=nonce):
        return "这不是微信请求呢"

    logging.debug(request.args)
    logging.debug(request.data)

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
