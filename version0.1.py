import os,sys
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from time import sleep

#保存文件
def SaveFile(fpath,fileContent):
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(fileContent)
        
#读取文件
def ReadFile(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        all_the_text = f.read()
    return all_the_text

#时间戳转日期
def Timestamp2Datetime(stampstr):
    dt = datetime.utcfromtimestamp(stampstr)
    dt = dt + timedelta(hours=8)
    newtimestr = dt.strftime("%Y%m%d_%H%M%S")
    return newtimestr

#下载url网页
def DownLoadHtml(url):
    #构造请求头
    headers = {
                     'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                     'Connection':'keep-alive',
                     'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
              } 
     
    response = requests.get(url,headers = headers)
    if response.status_code == 200:
        htmltxt = response.text #返回的网页正文
        return htmltxt
    else:
        return None

#将图片从远程下载保存到本地
def DownImg(url,savepath):
    r = requests.get(url)
    with open(savepath, 'wb') as f:
        f.write(r.content)

#修改网页中图片的src，使图片能正常显示
def ChangeImgSrc(htmltxt,saveimgdir,htmlname):
    bs =BeautifulSoup(htmltxt,"lxml") #由网页源代码生成BeautifulSoup对象，第二个参数固定为lxml
    imgList = bs.findAll("img")
    imgindex = 0
    for img in imgList:
        imgindex += 1
        originalURL = ""  # 图片真实url
        if "data-src" in img.attrs:#有的<img 标签中可能没有data-src
            originalURL = img.attrs['data-src']
        elif "src" in img.attrs:#如果有src则提取出来
            originalURL = img.attrs['src']
        else:
            originalURL = ""
        if originalURL.startswith("//"):#如果url以//开头，则需要添加http：
            originalURL = "http:" + originalURL
        if len(originalURL) > 0:
            print("down img",imgindex)
            if "data-type" in img.attrs:
                imgtype = img.attrs["data-type"]
            else:
                imgtype = "png"
            imgname = htmlname + "_"+str(imgindex)+"."+imgtype #形如 1.png的图片名
            imgsavepath = os.path.join(saveimgdir, imgname)  # 图片保存目录
            DownImg(originalURL,imgsavepath)
            img.attrs["src"] = "images/" + imgname #网页中图片的相对路径
        else :
            img.attrs["src"] = ""
    ChangeCssSrc(bs) #修改link标签
    return str(bs) #将BeautifulSoup对象再转换为字符串，用于保存

def ChangeCssSrc(bs):
    linkList = bs.findAll("link")
    for link in linkList:
        href = link.attrs["href"]
        if href.startswith("//"):
            newhref = "http:" + href
            link.attrs["href"] = newhref

#文章类
class Article():
    def __init__(self,url,pubdate,idx,title):
        self.url = url
        self.pubdate = pubdate
        self.idx = idx
        self.title = title

#从fiddler保存的json文件中提取文章url等信息
def GetArticleList(jsondir):
    filelist = os.listdir(jsondir)
    ArtList = []
    for file in filelist:
        filepath = os.path.join(jsondir,file)
        filetxt = ReadFile(filepath)
        jsbody = json.loads(filetxt)
        general_msg_list = jsbody["general_msg_list"]
        jsbd2= json.loads(general_msg_list)
        list = jsbd2["list"]
        for item in list: #一个item里可能有多篇文章
            artidx = 1 #请注意这里的编号只是为了保存html方便，并不对应于真实的文章发文位置(比如头条、次条、3条)
            comm_msg_info = item["comm_msg_info"]
            app_msg_ext_info = item["app_msg_ext_info"]
            pubstamp = comm_msg_info["datetime"]
            pubdate = Timestamp2Datetime(pubstamp)
            if comm_msg_info["type"] == 49: #49为普通图文类型，还有其他类型，暂不考虑
                url = app_msg_ext_info["content_url"] #文章链接
                idx = artidx
                title = app_msg_ext_info["title"]
                art = Article(url,pubdate,idx,title)
                ArtList.append(art)
                print(len(ArtList),pubdate, idx, title)
            if app_msg_ext_info["is_multi"] == 1: # 一次发多篇
                artidx += 1
                multi_app_msg_item_list = app_msg_ext_info["multi_app_msg_item_list"]
                for subArt in multi_app_msg_item_list:
                    url =subArt["content_url"]
                    idx =artidx
                    title = subArt["title"]
                    art = Article(url,pubdate,idx,title)
                    ArtList.append(art)
                    print(len(ArtList),pubdate, idx, title)
    return ArtList
if __name__ == "__main__":
    dir = "C:/vWeChatFiles/rawlist/Dump-0805-15-00-45" #改成你自己的文件夹地址
    saveHtmlDir = "c:/vWeChatFiles/html/" #改成你自己的保存目录，如果没有要新建
    saveImgDir = "c:/vWeChatFiles/html/images/" #改成你自己的保存目录，如果没有要新建
    ArtList = GetArticleList(dir)
    ArtList.sort(key=lambda x:x.pubdate,reverse=True) #按日期倒序排列
    totalCount = len(ArtList)
    idx=0
    for art in ArtList:
        idx+=1
        artname = art.pubdate + "_" + str(art.idx)
        arthtmlname = artname + ".html"
        arthtmlsavepath = os.path.join(saveHtmlDir,arthtmlname)
        print(idx,"of",totalCount,artname,art.title)
        # 如果已经有了则跳过，便于暂停后续传
        if os.path.exists(arthtmlsavepath):
            print("exists",arthtmlsavepath)
            continue
        arthtmlstr = DownLoadHtml(art.url)
        arthtmlstr = ChangeImgSrc(arthtmlstr,saveImgDir,artname)
        SaveFile(arthtmlsavepath,arthtmlstr)

        sleep(3) #防止下载过快被微信屏蔽，间隔3秒下载一篇