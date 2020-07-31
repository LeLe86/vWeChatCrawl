import os,sys,json
import time,requests
import hashlib,time,urllib
from urllib.request import urlopen
from urllib import parse,request
import urllib.request as urllib2
from pprint import pprint

def SaveFile(fpath,fileContent):    
    with open(fpath,'w',encoding='UTF-8') as f:
        f.write(fileContent)
        


def run(token,customerid,starttime,bizlist):
    nowtime=str(int(time.time()))
    url="http://tst.xiaokuake.com/w/fetch/?customerid="+customerid+"&token="+token
    
    postdata = {'customerid': customerid,
                    'bizlist': bizlist,
                    'starttime': starttime,
                }
    poststr = json.dumps(postdata) #转成字符串
    headers = {'content-type': "application/json"}
    response = requests.post(url, data = poststr, headers = headers) #发送一个post请求
    pprint(response.text) #pprint是格式化显示的意思
    #SaveFile("a.txt",response.text)


token="93cO7O302oDS" #测试账号固定填这个
customerid = "weiyan" #测试账号固定填这个
starttime = 1591784106 #获取starttime至今的数据，但最多只能获取最近24小时内的
bizlist = [
"MzA5NDc1NzQ4MA==", #差评
"MzUxNjUxMTg3OA==", #占豪
"MjM5MjAxNDM4MA==" #人民日报
]
#测试版的biz列表只能是列表中这几个，正式版也是要提前确定好一批biz,先关注了这些号才能收到其最新推送
#如果公众号不固定，又想做到想查哪个号就立马能查的，需要用到另外的接口，可联系作者获取(但价格会比这种固定一批公众号的贵)
#联系方式 www.xiaokuake.com/w/fetch/

run(token,customerid,starttime,bizlist)
