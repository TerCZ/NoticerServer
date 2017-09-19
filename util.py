import hashlib


TOKEN = "LongAsHeLives"


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
