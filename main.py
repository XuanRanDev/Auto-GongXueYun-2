import datetime
import json
import os
import random
import sys
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
        "user-agent": getUserAgent(user)
    }
    res = requests.post(url=url, data=json.dumps(data), headers=headers2)
    return res.json()["data"][0]["planId"]


def getUserAgent(user):
    if user["user-agent"] != 'null':
        return user["user-agent"]

    return random.choice(
        ['Mozilla/5.0 (Android 11 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
         'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
         'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'])


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
        print("错误：无法找到配置文件,将从系统环境变量中读取信息！")
        return json.loads(os.environ.get("USERS", ""))
    return json.loads(allUser)


def save(user, userId: str, token: str, planId: str, country: str, province: str,
         address: str, signType: str = "START", description: str = "",
         device: str = "Android", latitude: str = None, longitude: str = None):
    text = device + signType + planId + userId + f"{country}{province}{address}"
    headers2 = {
        'roleKey': 'student',
        "user-agent": getUserAgent(user),
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
        "user-agent": getUserAgent(user)
    }
    res = requests.post(url=url, data=json.dumps(data), headers=headers2)
    return res.json()


def useUserTokenSign(user):
    phone = user["phone"]
    token = user["token"]
    userId = user["userId"]
    planId = user["planId"]
    signStatus = startSign(userId, token, planId, user, startType=0)
    if signStatus:
        print('警告：保持登录失败，Token失效，请及时更新Token')
        print('重试：正在准备使用账户密码重新签到')
        MessagePush.pushMessage(phone, '工学云设备Token失效',
                                '工学云自动打卡设备Token失效，本次将使用账号密码重新登录签到，请及时更新配置文件中的Token' +
                                ',如不再需要保持登录状态,请及时将配置文件中的keepLogin更改为False取消保持登录打卡，如有疑问请联系微信：XuanRan_Dev'
                                , user["pushKey"])
        prepareSign(user, keepLogin=False)


def prepareSign(user, keepLogin=True):
    if not user["enable"]:
        return

    if user["keepLogin"] and keepLogin:
        # 启用了保持登录状态，则使用设备Token登录
        print('用户启用了保持登录，准备使用设备Token登录')
        useUserTokenSign(user)
        return

    userInfo = getToken(user)
    phone = user["phone"]

    if userInfo["code"] != 200:
        print('打卡失败，错误原因:' + userInfo["msg"])
        MessagePush.pushMessage(phone, '工学云打卡失败！',
                                '用户：' + phone + ',' + '打卡失败！错误原因：' + userInfo["msg"],
                                user["pushKey"])
        return

    userId = userInfo["data"]["userId"]
    token = userInfo["data"]["token"]

    sign = getSign2(userId + 'student')
    planId = get_plan_id(token, sign)
    startSign(userId, token, planId, user, startType=1)


# startType = 0 使用保持登录状态签到
# startType = 1 使用登录签到
def startSign(userId, token, planId, user, startType):
    hourNow = datetime.datetime.now(pytz.timezone('PRC')).hour
    if hourNow < 12:
        signType = 'START'
    else:
        signType = 'END'
    phone = user["phone"]
    print('-------------准备签到--------------')

    latitude = user["latitude"]
    longitude = user["longitude"]
    if user["randomLocation"]:
        latitude = latitude[0:len(latitude) - 1] + str(random.randint(0, 10))
        longitude = longitude[0:len(longitude) - 1] + str(random.randint(0, 10))

    signResp, msg = save(user, userId, token, planId,
                         user["country"], user["province"], user["address"],
                         signType=signType, description='', device=user['type'],
                         latitude=latitude, longitude=longitude)
    if signResp:
        print('签到成功')
    else:
        print('签到失败')
        if not startType:
            print('-------------签到完成--------------')
            return True

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

    print('-------------签到完成--------------')


def signCheck(users):
    for user in users:
        if not user["signCheck"] and user["enable"]:
            continue

        url = "https://api.moguding.net:9000/attendence/clock/v1/listSynchro"
        if user["keepLogin"]:
            print('保持登录状态开启，无需重新登录')
            token = user["token"]
        else:
            token = getToken(user)["data"]["token"]
        header = {
            "accept-encoding": "gzip",
            "content-type": "application/json;charset=UTF-8",
            "rolekey": "student",
            "host": "api.moguding.net:9000",
            "authorization": token,
            "user-agent": getUserAgent(user)
        }
        t = str(int(time.time() * 1000))
        data = {
            "t": encrypt("23DbtQHR2UMbH6mJ", t)
        }
        res = requests.post(url=url, headers=header, data=json.dumps(data))

        if res.json()["msg"] != 'success':
            print('获取打卡记录失败，请检查')
            continue

        lastSignInfo = res.json()["data"][0]
        lastSignDate = lastSignInfo["dateYmd"]
        lastSignType = lastSignInfo["type"]
        hourNow = datetime.datetime.now(pytz.timezone('PRC')).hour
        nowDate = str(datetime.datetime.now(pytz.timezone('PRC')))[0:10]
        if hourNow <= 12 and lastSignType == 'END' and lastSignDate != nowDate:
            print('今日未打上班卡，准备补签')
            prepareSign(user)
        if hourNow >= 18 and lastSignType == 'START' and lastSignDate == nowDate:
            print('今日未打下班卡，准备补签')
            prepareSign(user)
        print('打卡检查运行完成...')
        continue


if __name__ == '__main__':
    users = parseUserInfo()
    hourNow = datetime.datetime.now(pytz.timezone('PRC')).hour
    if hourNow == 11 or hourNow == 18:
        # 今日打卡检查
        signCheck(users)
        sys.exit()
    for user in users:
        try:
            prepareSign(user)
        except Exception as e:
            MessagePush.pushMessage(user["phone"], '工学云打卡失败',
                                    '工学云打卡失败, 可能是连接工学云服务器超时。'
                                    , user["pushKey"])
