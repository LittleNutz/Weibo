# -*- codeing = utf-8 -*-
# @Time : 2021/3/16 18:09
# @software: PyCharm

import re
import os
from bs4 import BeautifulSoup
import urllib.request,urllib.error,urllib.parse
import datetime
import  json


cookie = 'SINAGLOBAL=4528122394319.048.1600936936249; _ga=GA1.2.833437142.1606195636; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh5PKh7NpCZ1znsvzEpYGqu5JpX5KMhUgL.Fo-01heNe050eKM2dJLoIEYLxKBLB.eL1-2LxK.LBKeL1--LxKML1-2L1hBLxKML12zLB--LxK-LB-BL1KWkP7tt; UM_distinctid=17854adad36143-0abd0d21be5f7a-5771031-1fa400-17854adad374b2; wvr=6; UOR=,,login.sina.com.cn; ALF=1648367161; SSOLoginState=1616831162; SCF=Ak6xHWie_7adbXRb51tgHc9nV-h5buq8TGL2GFbh7v91DODM5GYnrbuuI4F3qkqRMxrZwV_DuywP-h8U0XaBIgE.; SUB=_2A25NWpLqDeRhGeNN41EW8y7PyjuIHXVuEYMirDV8PUNbmtANLWnVkW9NSXm5CipMZh9II30XECN4IN_5mZubklNX; _s_tentry=weibo.com; Apache=1126419880609.8257.1616831167788; ULV=1616831168165:46:22:9:1126419880609.8257.1616831167788:1616651077349; WBStorage=8daec78e6a891122|undefined'
def main():
    baseurl = 'https://photo.weibo.com/photos/get_all?6697930990&album_id=4283828063672324&count=100&page=1&type=&__rnd=1504068705105'
    savepath = "D:/一尾阿梓Azusa/"
    file = open(savepath + "信息.txt", 'r')
    js = file.read()
    opdata = json.loads(js)
    file.close()
    print('-' * 5, '%s' % opdata['name'], '-' * 5, end='\n')
    print('-' * 5, '保存图片', '-' * 5, end='\n')

    imglink,imgdate = allData(baseurl,opdata)
    saveimg(imglink,imgdate,savepath)

    opdata["lastdate"] = imgdate[0]
    opdata["lastlink"] = imglink[0]
    opdata["lastsave"] = str(datetime.date.today())
    opdata["picsum"] = opdata["picsum"] + len(imglink)
    print('目前共有 %d 张图片'%opdata['picsum'])
    with open(savepath + "信息.txt", 'w') as f:
        json_str = json.dumps(opdata, indent=0)
        f.write(json_str)
        f.close()
    print('-' * 5,"保存完毕！",'-' * 5)
 #   askURL(baseurl)

findLink = re.compile(r'"pic_name":"(.*?)"',re.S)
findtotal = re.compile(r'"total":(.*?),')
finddata = re.compile(r'"created_at":"(.*?)"')

#整合所有图片信息
def allData(basurl,opdata):
    i = 1
    flag = 1
    alllink = []
    alldate = []
    while flag == 1:
        url = basurl.replace('page=1','page=%d'%i)
        link,date = getData(url)
        if len(link) == 0:
            break
        print('正在读取第 %d 页图片'%i)
        dateflag = date[-1]
        dateflag = int(dateflag.replace('-',''))
        lastdate = int(opdata['lastdate'].replace('-',''))
        if dateflag < lastdate:
            if opdata['lastlink'] in link:
                numflag = link.index(opdata['lastlink'])
                flag = 0
            else:
                datefirst = int(date[0].replace('-',''))
                if datefirst >= lastdate:
                    j = 0
                    dateflag2 = int(date[0].replace('-',''))
                    while dateflag2 >= lastdate:
                        j = j + 1
                        dateflag2 = int(date[j].replace('-', ''))
                    numflag = date.index(date[j]) - 1
                    flag = 0
                else:
                    numflag = 0
                    flag = 0
        elif dateflag == lastdate:
            if opdata['lastlink'] in link:
                numflag = link.index(opdata['lastlink'])
                flag = 0
        if flag == 1:
            alllink = alllink + link
            alldate = alldate + date
        elif flag == 0:
            alllink = alllink + link[0:numflag]
            alldate = alldate + date[0:numflag]
        i = i + 1

    return alllink,alldate





#获取单页相册的图片信息
def getData(basurl):
    url = basurl
    html = askURL(url)  #保存获取到的网页源码
    #逐一解析网页
    soup = BeautifulSoup(html,"html.parser")
    soup = str(soup)
    link = re.findall(findLink,soup)  # re库用来通过正则表达式查找指定字符串,findall匹配出来为列表格式
    date = re.findall(finddata,soup)
    if len(date) != 0:
        if date[0].find('\\u') != -1 : #判断图片发表日期是否解码
            date = Changedate(date)
    return link,date

#得到一个指定URL的网页内容
def askURL(url):
    head = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        "cookie": cookie
    }
    request = urllib.request.Request(url,headers=head)
    html=""
    try:
        response = urllib.request.urlopen(request)
        #html = response.read()
        html = response.read().decode("utf-8")
        #print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
 #   print(html)
    return html

#保存图片
def saveimg(link,date,savepathbase):
    opener = urllib.request.build_opener()
    opener.addheaders = [("user-agent","Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36")]
    urllib.request.install_opener(opener)   #储存图片时加入请求头，绕过反爬
    imgsum = len(link)
    savepath = savepathbase + date[0][0:7] + '/'
    if os.path.exists(savepath):
        pass
    else:
        os.makedirs(savepath)
    downlink = 'https://wx4.sinaimg.cn/large/' + link[0]
    print('正在保存第 %d /%d 张图片....' % (1, imgsum))
    datepath = '[' + date[0].replace('-', '.') + ']'
    urllib.request.urlretrieve(downlink, savepath + datepath + link[0])

    for i in range(1,len(link)):
        savepathflag = date[i-1][0:7]
        datepath = '[' + date[i].replace('-','.') +']'
        if date[i][0:7] == savepathflag:
            downlink = 'https://wx4.sinaimg.cn/large/' + link[i]
            print('正在保存第 %d /%d 张图片....'%(i+1,imgsum))
            urllib.request.urlretrieve(downlink, savepath + datepath + link[i])
        else:
            savepath = savepathbase + date[i][0:7] + '/'
            if os.path.exists(savepath):
                pass
            else:
                os.makedirs(savepath)
            downlink = 'https://wx4.sinaimg.cn/large/' + link[i]
            print('正在保存第 %d /%d 张图片....'%(i+1,imgsum))
            urllib.request.urlretrieve(downlink, savepath + datepath + link[i])

#日期信息解码并替换
def Changedate(date):
    today = datetime.date.today()
    today = str(today)
    for i in range(0,len(date)):
        date[i] = date[i].encode('utf-8').decode('unicode-escape')
        monnum = date[i].find('月')
        daynum = date[i].find('日')
        if monnum != -1:
            year = today[0:4]
            mon = date[i][0:monnum]
            day = date[i][monnum+1:daynum]
            mon = mon.zfill(2)
            day = day.zfill(2)
            date[i] = '%s-%s-%s'%(year,mon,day)
        elif date[i].find('今天') != -1:
            date[i] = today
    return date






if __name__ == "__main__":
    main()