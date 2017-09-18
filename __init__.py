#!/usr/bin/python3
# -*- coding: <encoding name> -*-
from flask import Flask, request


app = Flask(__name__)


@app.route("/")
def hello_world():
<<<<<<< HEAD
    s = request["signature"]
    s += request["timestamp"]
    s += request["nonce"]
    s += request["echostr"]

=======
>>>>>>> aa0d94030947c568844f79402abd180e10d56c35
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

<<<<<<< HEAD
    return s
=======
    return str(request.form) + "\n" + str(request.args)
>>>>>>> aa0d94030947c568844f79402abd180e10d56c35

if __name__ == "__main__":
    app.run()
