# -*- codeing = utf-8 -*-
# @Time : 2021/3/19 17:15
# @software: PyCharm

import re
import os
from bs4 import BeautifulSoup
import urllib.request,urllib.error,urllib.parse
import requests
import time
import json

#爬取不同bo主视频只需改动firsturl和savepath

cookie = 'SINAGLOBAL=4528122394319.048.1600936936249; _ga=GA1.2.833437142.1606195636; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh5PKh7NpCZ1znsvzEpYGqu5JpX5KMhUgL.Fo-01heNe050eKM2dJLoIEYLxKBLB.eL1-2LxK.LBKeL1--LxKML1-2L1hBLxKML12zLB--LxK-LB-BL1KWkP7tt; UM_distinctid=17854adad36143-0abd0d21be5f7a-5771031-1fa400-17854adad374b2; wvr=6; UOR=,,login.sina.com.cn; ALF=1648367161; SSOLoginState=1616831162; SCF=Ak6xHWie_7adbXRb51tgHc9nV-h5buq8TGL2GFbh7v91DODM5GYnrbuuI4F3qkqRMxrZwV_DuywP-h8U0XaBIgE.; SUB=_2A25NWpLqDeRhGeNN41EW8y7PyjuIHXVuEYMirDV8PUNbmtANLWnVkW9NSXm5CipMZh9II30XECN4IN_5mZubklNX; TC-V-WEIBO-G0=35846f552801987f8c1e8f7cec0e2230; _s_tentry=weibo.com; Apache=1126419880609.8257.1616831167788; ULV=1616831168165:46:22:9:1126419880609.8257.1616831167788:1616651077349; XSRF-TOKEN=yzXPsyq3TFZY_NHnf004t66p; WBPSESS=2EzaQ5g-6pnS48T5Zp0l5DYmNAZQvQhvH7Ed1MXP1OrjhCn76PCatxNbFBuqklJjiwktZtYpNb3h3Z7zO3xTL-8a3rR9IHskMr8tV1Ym4Nyjawv53p-62aFk9-WO_FaY'

def main():
    firsturl="https://weibo.com/p/1005056697930990/photos?type=video#place"
    savepath = "D:/一尾阿梓Azusa/VID/"
    file = open("D:/一尾阿梓Azusa/信息.txt", 'r')
    js = file.read()
    opdata = json.loads(js)
    file.close()
    lastlink = opdata['lastvidlink']
    alllink = getAllPage(firsturl,lastlink)
    getAllvideo(alllink,savepath)
    opdata['lastvidlink'] = alllink[0]
    opdata['vidsum'] = opdata['vidsum'] + len(alllink)
    with open("D:/一尾阿梓Azusa/信息.txt", 'w') as f:
        json_str = json.dumps(opdata, indent=0)
        f.write(json_str)
        f.close()
    print('-' * 5,"保存完毕！",'-' * 5)


findLink = re.compile(r'<img alt=.*?src="(.*?)" title=".*?>',re.S)
findFirstpage = re.compile(r'<a target=\\"_blank\\" href=\\"(https:\\/\\/video.*?)\\">',re.S)
findpage = re.compile(r'<a href=.\\"(.*?)\\". target=.\\"_blank\\".>',re.S)
findpageid = re.compile(r'https://weibo.com/p/(.*?)/photos.type=video#place')
findjiao = re.compile(r'<.*?>')


def getAllPage(firsturl,lastlink):
    opener = urllib.request.build_opener()
    opener.addheaders = [("user-agent","Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36")]
    urllib.request.install_opener(opener)   #储存图片时加入请求头，绕过反爬
    alllink = getFirstPage(firsturl)
    pageid = re.findall(findpageid,firsturl)[0]
    mid,uid = askvidmid(alllink[-1])
    flag = 1
    for i in range(0,len(alllink)):
        if lastlink == alllink[i]:
            alllink = alllink[0:i]
            flag = 0
            break
    while flag == 1:
        link = getpage(pageid,mid,uid)
        mid,uid = askvidmid(link[-1])
        for i in range(0, len(link)):
            if lastlink == link[i]:
                link = link[0:i]
                flag = 0
                break
        if len(link) != 1:
            alllink = alllink +link[1:]
        else:
            flag = 0
    return alllink


def getAllvideo(alllink,savepath):
    if os.path.exists(savepath):
        pass
    else:
        os.makedirs(savepath)
    print(alllink)
    for i in range(0,len(alllink)):
        vidlink,text = askvid(alllink[i])
        print('正在保存第 %d /%d 个视频'%(i+1,len(alllink)))
        urllib.request.urlretrieve('http:' + vidlink, savepath + text + '.mp4')




#得到第一页相册中视频链接
def getFirstPage(url):
    html = askpageURL(url)  #保存获取到的网页源码
    #逐一解析网页
    soup = BeautifulSoup(html,"html.parser")
    soup = str(soup)
    link = re.findall(findFirstpage,soup)
    for i in range(0,len(link)):
        link[i] = link[i].replace('\\','')
    link = sorted(set(link),key=link.index)
    return link


#得到后续页相册视频链接
def getpage(pageid,mid,uid):
    url = "https://weibo.com/p/aj/album/loading?ajwvr=6&type=video&owner_uid=%s&viewer_uid=5383730317&since_id=%s&page_id=%s&page=2&ajax_call=1"%(uid,mid,pageid)
    html = askpageURL(url)  #保存获取到的网页源码
    #逐一解析网页
    soup = BeautifulSoup(html,"html.parser")
    soup = str(soup)
    link = re.findall(findpage,soup)
    for i in range(0,len(link)):
        link[i] = link[i].replace('\\','')
    link = sorted(set(link),key=link.index)
    return link


#得到相册页面内容
def askpageURL(url):
    head = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        'Content-Type': 'application/x-www-form-urlencoded',
        "cookie": cookie
    }
    request = urllib.request.Request(url,headers=head)
    html=""
    try:
         response = urllib.request.urlopen(request)
         html = response.read().decode("utf-8")
     #   print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html

#得到视频mid
def askvidmid(link):
    url = "https://weibo.com/tv/api/component"
    oid = link[33:]
    head = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        'Content-Type': 'application/x-www-form-urlencoded',
        'referer': 'https://weibo.com/tv/show/%s?from=old_pc_videoshow'%oid,
        "cookie": cookie
    }
    params = {
        'page': '/tv/show/%s'%oid
    }
    data = {
        'data': '{"Component_Play_Playinfo":{"oid":"%s"}}'%oid
    }
    request = requests.post(url, params=params, data=data, headers=head).json()
    mid = request['data']['Component_Play_Playinfo']['mid']
    uid = request['data']['Component_Play_Playinfo']['user']['id']
    return mid,uid

def askvid(link):
    url = "https://weibo.com/tv/api/component"
    oid = link[33:]
    head = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        'Content-Type': 'application/x-www-form-urlencoded',
        'referer': 'https://weibo.com/tv/show/%s?from=old_pc_videoshow'%oid,
        "cookie": cookie
    }
    params = {
        'page': '/tv/show/%s'%oid
    }
    data = {
        'data': '{"Component_Play_Playinfo":{"oid":"%s"}}'%oid
    }
    request = requests.post(url, params=params, data=data, headers=head).json()
    vidlink = list(request['data']['Component_Play_Playinfo']['urls'].values())[0]
    text = request['data']['Component_Play_Playinfo']['text']
    text = re.sub(findjiao, '', text)
    text = text.replace(' ', '')
    if len(text) > 10:
        text = text[0:10]
    title = request['data']['Component_Play_Playinfo']['title']
    #title = title.replace(' ', '')
    short = request['data']['Component_Play_Playinfo']['url_short']
    short = short.replace('http://t.cn/','')
    text = title + ' ' + text
    text = text.replace('\\u200b','')
    text = text + ' ' + short

    timetamp = request['data']['Component_Play_Playinfo']['real_date']
    timetamp = int(timetamp)
    timeArray = time.localtime(timetamp)
    date = time.strftime("%Y.%m.%d", timeArray)

    date = '[' + date +']'
    text = date +text

    return vidlink,text


if __name__ == "__main__":
    main()