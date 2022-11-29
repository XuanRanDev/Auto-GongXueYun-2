<div align="center">
<h1 align="center">
Auto-GongXueYun
</h1>
<p align="center">
🥰工学云自动打卡解决方案🥰
</p>
<p align="center">
支持多用户、自定义位置信息、保持登录状态、每日打卡检查
</br>
打卡位置浮动、自定义UA、微信消息推送、自动填写周报（TODO）
</br>
</p>
</br>
<a target="_blank" href="https://www.bilibili.com/video/BV1VP4y117w8/?spm_id_from=333.999.0.0&vd_source=23b414916f0ead82eaa42a85d58614c8">视频教程</a>
</div>
</br>



## 前言

**1、请务必认真阅读此文档后继续！**

**2、本项目开源&免费，所有开发均仅限于学习交流，禁止用于任何商业用途。**

**3、在开始之前请务必帮我点一下右上角的star。**

**4、最新发行版（正式版）及更新日志请参见[Release](https://github.com/XuanRanDev/Auto-GongXueYun/releases/tag/v1.0)。**


</br>


## 目录

- [前言](#前言)
- [使用门槛](#使用门槛)
- [使用方法](#使用方法)
  - [Github Actions](#github-actions)
  - [使用自己的服务器部署](#使用自己的服务器部署)
- [启用保持登录](#启用保持登录)
- [启用每日打卡检查](#启用每日打卡检查)
- [启用打卡位置浮动](#启用打卡位置浮动)
- [修改自动打卡时间🎯](#修改自动打卡时间)
- [赞助支持](#赞助支持)
- [常见问题](#常见问题)
  - [打卡失败](#打卡失败)

</br>
</br>

## 使用门槛

帮我点一下右上角的star（星星）



</br></br>

## 使用方法

### Github Actions

推荐指数：⭐⭐⭐⭐⭐


优点：适合没有自己服务器的人使用。


缺点：

1、每日打卡时间无法保证十分准时，拥有10-30分钟的误差。

2、Action在某些情况下可能会连接工学云服务器超时造成打卡失败(已加入每日打卡检查，当未打卡时会补签)。

</br>

1.点击Star后Fork本仓库🤪

![1.png](https://tc.xuanran.cc/2022/11/13/1932d085c97c2.png)
![2.png](https://tc.xuanran.cc/2022/11/13/c6e9abebb113c.png)
</br>
2.准备配置文件🤔

如果想同时打卡多个用户,请再添加一个数据体就好了(如果还不理解加我微信（XuanRan_Dev）（记得备注来意）我教你)

**注意：配置文件模板下方有配置含义，请务必参照配置含义填写**
```json
[
  {
    "enable": true,
    "phone": "17666666666",
    "password": "1111111111",
    "keepLogin": false,
    "token": "如果keepLogin为false就不填",
    "userId": "如果keepLogin为false就不填",
    "planId": "如果keepLogin为false就不填",
    "randomLocation": true,
    "user-agent": "null",
    "signCheck": false,
    "country": "中国",
    "province": "河南省",
    "city": "洛阳市",
    "type": "android",
    "address": "你的详细地址",
    "latitude": "33.1000354488",
    "longitude": "101.57487848",
    "pushKey": "dhsajifysfsafsdfdsxxxxxx"
  }
]

```

其配置含义如下：

| 参数名称       | 含义                                                         |
| -------------- | ------------------------------------------------------------ |
| enable         | 是否启用该用户的打卡（true或false)                           |
| phone          | 手机号                                                       |
| password       | 密码                                                         |
| keepLogin      | 是否启用保持登录，启用后程序每次打卡将不再重新登录，避免挤掉手机工学云的登录，启用后请通过抓包工学云获取你的token、userId、planId然后填写在下方 |
| token          | 如果keepLogin启用，则在此填写你的token                       |
| userId         | 如果keepLogin启用，则在此填写你的userId                      |
| planId         | 如果keepLogin启用，则在此填写你的planId                      |
| randomLocation | 是否启用打卡位置浮动，启用后每次打卡会在原有位置基础上进行位置浮动 |
| user-agent     | 是否自定义UA，如果不需要自定义填null（字符串形式），否则填写你的UA（[可以点我随便选一个](https://wp.xuanran.cc/s/JBTA)） |
| signCheck      | 每日签到检查,某些情况下action可能没网络造成打卡失败,启用此选项后,将在每日11点以及23点检查今日的打卡状态,如未打卡则补卡 |
| country        | 国家                                                         |
| province       | 省份                                                         |
| city           | 城市                                                         |
| type           | android 或 ios                                               |
| address        | 详细地址，详细地址开头最好加上市，比如说洛阳市西工区xxx街道  |
| latitude       | 打卡位置纬度,通过坐标拾取来完成(仅需精确到小数点后6位)，[传送门](https://jingweidu.bmcx.com/) |
| longitude      | 打卡位置精度,通过坐标拾取来完成(仅需精确到小数点后6位)，[传送门](https://jingweidu.bmcx.com/) |
| pushKey        | 打卡结果微信推送，微信推送使用的是pushPlus，请到官网绑定微信([传送门](https://www.pushplus.plus/))，然后在发送消息里面把你的token复制出来粘贴到pushKey这项 |



</br>

3.配置Secret

填写完成后请复制如上配置文件，然后打开仓库的Settings->Secrets->Actions->New repository secret

Name填USERS

Secret填改好的配置文件

![3.png](https://tc.xuanran.cc/2022/11/13/2143b390f8199.png)
![4.png](https://tc.xuanran.cc/2022/11/13/8de9cb85e479b.png)

4.运行测试
![5.png](https://tc.xuanran.cc/2022/11/13/500e789b3dfec.png)
![6.png](https://tc.xuanran.cc/2022/11/13/1366e5e0ced97.png)
![7.png](https://tc.xuanran.cc/2022/11/13/2a2b4b7e01884.png)
![8.png](https://tc.xuanran.cc/2022/11/13/bd1cd3218f77a.png)
![9.png](https://tc.xuanran.cc/2022/11/13/33c6cec2e37ec.png)
![10.png](https://tc.xuanran.cc/2022/11/13/a9e80f17d304b.png)
</br></br></br></br>

至此，自动打卡将会在每天7点和18点左右自动运行打卡。😉


</br></br></br>

### 使用自己的服务器部署

推荐指数：⭐⭐

优点：运行稳定、准时。

缺点：有一定的上手成本。

具体教程：

1、下载本仓库源码到你服务器。

2、在服务器中安装好Python环境。

3、运行命令来下载依赖。

```python
pip install pytz
pip install pycryptodome
```

4、在百度搜索：你的操作系统+ 定时任务，查看如何创建定时任务。

5、创建一个user.json配置文件在项目目录，并将配置文件放入其中

6、运行python main.py测试

</br></br></br>




## 启用保持登录
启用保持登录指的是打卡程序在启用保持登录开启后不再使用账号密码登录打卡，而是使用Token方式。

启用保持登录需要会抓包，而且要抓https的包，如果你手机没Root就别想了

1、下载小黄鸟，抓包软件选择工学云

2、打开工学云

3、在抓包软件里找到https://api.moguding.net/attendence/clock/v1/listSynchro
这个请求

4、找到Token以及userId、planId
![11](https://tc.xuanran.cc/2022/11/13/520b118fe371a.jpg)
![12](https://tc.xuanran.cc/2022/11/13/ec400140df3d8.jpg)



</br></br>


## 启用每日打卡检查
因为Github Action某些情况下可能会无法连接工学云服务器造成打卡+推送失败问题，为此推出每日打卡检查，启用后，每日11点（有1次检查）以及23点（也有1次检查）将会对今日打卡情况进行分析，如存在漏签则自动补签。

如需开启，请在配置文件中的signCheck设置为true
</br></br>


## 启用打卡位置浮动
启用打卡位置浮动后，每次打卡系统会在原有经纬度中删掉最后一位数字，并随机加入一位数字，使每次打卡经纬度不同。
</br></br>

## 修改自动打卡时间🎯	

修改自动打卡时间需要了解Cron表达式的使用，且需注意不要将打卡时间设置为11点以及23点，此时间段中会运行每日打卡检查，自动打卡在此时间段内不生效。😴


</br>
1.编辑sign.yml文件，找到图中我圈出的部分

![image-20221021093411661](https://tc.xuanran.cc/2022/11/10/5d81dcc0bff46.png)

</br>

2.编辑表达式

GitHub的cron表达式不支持精准到秒，所以从最左边开始，分别为：

分钟 小时 日 月份 星期

而且Github的服务器时间会比我们晚八个小时，所以在你需要打卡的时间-8配置到里面就行了

</br>

例如说在上午十点打上班卡就是:

```yml
- cron: "00 2 * * *"
```



晚上九点打下班卡：

```yml
- cron: "00 13 * * *"
```

</br>
</br>





## 赞助支持

如果此仓库帮助了你学到了新知识，你可以帮我买杯可乐。

![赞助支持](https://tc.xuanran.cc/2022/11/20/b8f5ddc944634.png)



## 常见问题

### 打卡失败 

如果遇到action运行失败或者打卡失败，99%都是连接工学云服务器超时了，重新运行下action就行了，这点没很好的处理办法，我已经在代码中加入了两次的重试还不行，这是Github的问题。






</br></br>
最后，帮我点下仓库的小星星，Thanks.

😀😀😀😀😀
