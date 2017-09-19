#!/usr/bin/python3
# -*- coding: <encoding name> -*-
from flask import Flask, request
import hashlib

app = Flask(__name__)


@app.route("/", methods=["GET"])
def hello_world():
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    echostr = request.args.get("echostr", "")
    token = "LongAsHeLives"

    args = [token, timestamp, nonce]
    args.sort()
    sha1 = hashlib.sha1()
    map(sha1.update, args)
    hashcode = sha1.hexdigest()
    if hashcode == signature:
        return echostr
    else:
        return "这不是微信请求呢"


if __name__ == "__main__":
    app.run()
