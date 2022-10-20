import json
import os
import time
from hashlib import md5
import sys
import pytz
import datetime
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

pwd = os.path.dirname(os.path.abspath(__file__)) + os.sep


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
    return res.json()["code"] == 200


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


if __name__ == '__main__':
    hourNow = datetime.datetime.now(pytz.timezone('PRC')).hour
    print(hourNow)
    sys.exit()
    users = parseUserInfo()
    for user in users:

        userInfo = getToken(user)
        if userInfo["code"] != 200:
            print(userInfo["msg"])
            continue
        print('已登录：', user["phone"])
        print(userInfo)

        userId = userInfo["data"]["userId"]
        moguNo = userInfo["data"]["moguNo"]
        token = userInfo["data"]["token"]

        sign = getSign2(userId + 'student')
        planId = get_plan_id(token, sign)
        print('-------------', user["phone"], ':准备签到--------------')
        signResp = save(userId, token, planId,
                        user["country"], user["province"], user["address"],
                        signType='START', description='', device=user['type'],
                        latitude=user["latitude"], longitude=user["longitude"])
        if signResp:
            print(user["phone"], ':签到成功')
        else:
            print(user["phone"], ':签到失败')
        print('-------------', user["phone"], ':签到完成--------------')

