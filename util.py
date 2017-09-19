import hashlib
from time import time


TOKEN = "LongAsHeLives"
DEFAULT_PROMPT = "欢迎使用SJTU Noticer校园信息订阅服务！通过微信号您可以管理您的订阅，我们将为您定期通过邮件推送最新校园通知。\n\n您可以发送以下消息进行操作：\n「邮箱 your@email.com」，注册（或更新）您的邮箱，请替换your@email.com为您的邮箱；\n「信息来源」查看当前可用的信息来源；\n「订阅 7」，开启订阅并设置（或更新）推送周期为7天，请替换7为您偏好的推送周期；\n「取消」，取消当前的邮件推送，您的订阅设置不会被删除。\n\n您也可以通过留言进行反馈，帮助我们做得更好！"

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
