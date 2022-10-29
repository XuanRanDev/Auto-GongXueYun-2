import datetime
import json
import os
import time
from hashlib import md5

import pytz
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

import MessagePush

pwd = os.path.dirname(os.path.abspath(__file__)) + os.sep

# 设置重连次数
requests.adapters.DEFAULT_RETRIES = 5


def get_plan_id(token: str, sign: str):
    url = "https://api.moguding.net:9000/practice/plan/v3/getPlanByStu"
    data = {
        "state": ""
    }
    headers2 = {
        'roleKey': 'student',
        "authorization": token,
        "sign": sign,
        "content-type": "application/json; charset=UTF-8",
        "user-agent": 'Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.2.3 (Baidu; P1 9)'
    }
    res = requests.post(url=url, data=json.dumps(data), headers=headers2)
    return res.json()["data"][0]["planId"]


def getSign2(text: str):
    s = text + "3478cbbc33f84bd00d75d7dfa69e0daa"
    return md5(s.encode("utf-8")).hexdigest()


def parseUserInfo():
    allUser = ''
    if os.path.exists(pwd + "user.json"):
        with open(pwd + "user.json", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                allUser = allUser + line + '\n'
    else:
        print("错误：无法找到配置文件")
        return
    return json.loads(allUser)


def save(userId: str, token: str, planId: str, country: str, province: str,
         address: str, signType: str = "START", description: str = "",
         device: str = "Android", latitude: str = None, longitude: str = None):
    text = device + signType + planId + userId + f"{country}{province}{address}"
    headers2 = {
        'roleKey': 'student',
        "user-agent": 'Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.2.3 (Baidu; P1 9)',
        "sign": getSign2(text=text),
        "authorization": token,
        "content-type": "application/json; charset=UTF-8"
    }
    data = {
        "country": country,
        "address": f"{country}{province}{address}",
        "province": province,
        "city": province,
        "latitude": latitude,
        "description": description,
        "planId": planId,
        "type": signType,
        "device": device,
        "longitude": longitude
    }
    url = "https://api.moguding.net:9000/attendence/clock/v2/save"
    res = requests.post(url=url, headers=headers2, data=json.dumps(data))
    return res.json()["code"] == 200, res.json()["msg"]


# 工学云加密算法
def encrypt(key, text):
    aes = AES.new(key.encode("utf-8"), AES.MODE_ECB)
    pad_pkcs7 = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
    res = aes.encrypt(pad_pkcs7)
    msg = res.hex()
    return msg


def getToken(user):
    url = "https://api.moguding.net:9000/session/user/v3/login"
    t = str(int(time.time() * 1000))
    data = {
        "password": encrypt("23DbtQHR2UMbH6mJ", user["password"]),
        "phone": encrypt("23DbtQHR2UMbH6mJ", user["phone"]),
        "t": encrypt("23DbtQHR2UMbH6mJ", t),
        "loginType": user["type"],
        "uuid": ""
    }
    headers2 = {
        "content-type": "application/json; charset=UTF-8",
        "user-agent": 'Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.20 SP-engine/2.16.0 baiduboxapp/11.20.2.3 (Baidu; P1 9)'
    }
    res = requests.post(url=url, data=json.dumps(data), headers=headers2)
    return res.json()


def prepareSign(user):
    userInfo = getToken(user)
    phone = user["phone"]

    if userInfo["code"] != 200:
        print(phone + ',打卡失败，错误原因:' + userInfo["msg"])
        MessagePush.pushMessage(phone, '工学云打卡失败！',
                                '用户：' + phone + ',' + '打卡失败！错误原因：' + userInfo["msg"],
                                user["pushKey"])
        return
    print('已登录：', phone)

    userId = userInfo["data"]["userId"]
    moguNo = userInfo["data"]["moguNo"]
    token = userInfo["data"]["token"]

    sign = getSign2(userId + 'student')
    planId = get_plan_id(token, sign)
    hourNow = datetime.datetime.now(pytz.timezone('PRC')).hour
    if hourNow < 12:
        signType = 'START'
    else:
        signType = 'END'
    print('-------------', phone, ':准备签到--------------')
    signResp, msg = save(userId, token, planId,
                         user["country"], user["province"], user["address"],
                         signType=signType, description='', device=user['type'],
                         latitude=user["latitude"], longitude=user["longitude"])
    if signResp:
        print(phone, ':签到成功')
    else:
        print(phone, ':签到失败')

    ######################################
    # 处理推送信息
    pushSignType = '上班'
    if signType == 'END':
        pushSignType = '下班'

    pushSignIsOK = '成功！'
    if not signResp:
        pushSignIsOK = '失败！'

    # 推送消息内容构建

    MessagePush.pushMessage(phone, '工学云' + pushSignType + '打卡' + pushSignIsOK,
                            '用户：' + phone + '，工学云' + pushSignType + '打卡' + pushSignIsOK
                            , user["pushKey"])

    # 消息推送处理完毕
    #####################################

    print('-------------', phone, ':签到完成--------------')


def retrySign(user, flag):
    if flag == 2:
        MessagePush.pushMessage(user['phone'], '工学云打卡失败',
                                '工学云打卡失败，请尝试手动打卡'
                                , user["pushKey"])
        return

    try:
        print('重试次数：', flag + 1)
        prepareSign(user)
    except Exception as e:
        retrySign(user, flag + 1)


if __name__ == '__main__':
    users = parseUserInfo()
    for user in users:
        try:
            prepareSign(user)
        except Exception as e:
            print(user['phone'], '签到失败，准备重试')
            retrySign(user, 0)
