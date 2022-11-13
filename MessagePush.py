import requests


# PushPlus
def pushMessage(phone, title, content, token):
    url = 'http://www.pushplus.plus/send?token=' + token + '&title=' + title + '&content=' + content + '&template=html'
    resp = requests.post(url)
    if resp.json()["code"] == 200:
        print('推送消息提醒成功！')
    else:
        print('推送消息提醒失败！')
