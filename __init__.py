#!/usr/bin/python3
# -*- coding: <encoding name> -*-
import hashlib
import logging

from flask import Flask, request


app = Flask(__name__)


@app.route("/", methods=["GET"])
def hello_world():
    app.logger.info("fuck from logger, {}".format(request.args))
    app.logger.info("fuck from logger, {}".format(request.args))
    print("fuck from print", request.args)
    
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    echostr = request.args.get("echostr", "")
    token = "LongAsHeLives"

    args = [token, timestamp, nonce]
    args.sort()
    sha1 = hashlib.sha1()
    sha1.update("".join(args).encode('utf-8'))
    hashcode = sha1.hexdigest()
    if hashcode == signature:
        return echostr
    else:
        return "这不是微信请求呢"


@app.route("/", methods=["POST"])
def receive_text():
    to_user_name = request.form.get("ToUserName")
    from_user_name = request.form.get("FromUserName")
    create_time = request.form.get("CreateTime")
    msg_type = request.form.get("MsgType")
    if msg_type == "text":
        content = request.form.get("Content")
        msg_id = request.form.get("MsgId")

        app.logger.debug("ToUserName: {}\tFromUserName: {}\tCreateTime: {}\tMsgType: {}\tContent: {}\tMsgId: {}\t".format(
            to_user_name, from_user_name, create_time, content, msg_id))

    return "success"


if __name__ == "__main__":
    app.run()
