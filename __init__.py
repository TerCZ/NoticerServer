#!/usr/bin/python3
# -*- coding: <encoding name> -*-
from flask import Flask, request


app = Flask(__name__)


@app.route("/")
def hello_world():
    # signature = data.signature
    # timestamp = data.timestamp
    # nonce = data.nonce
    # echostr = data.echostr
    # token = "xxxx"  # 请按照公众平台官网\基本配置中信息填写
    #
    # list = [token, timestamp, nonce]
    # list.sort()
    # sha1 = hashlib.sha1()
    # map(sha1.update, list)
    # hashcode = sha1.hexdigest()
    # print "handle/GET func: hashcode, signature: ", hashcode, signature
    # if hashcode == signature:
    #     return echostr
    # else:
    #     return ""

    return str(request.form) + "\n" + str(request.args)

if __name__ == "__main__":
    app.run()
