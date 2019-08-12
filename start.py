import os,sys
import requests
import json
import subprocess
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from time import sleep

"""
本项目开源地址 https://github.com/LeLe86/vWeChatCrawl

"""

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

#初始化环境
def GetJson():
    jstxt =ReadFile("config.json")
    jsbd = json.loads(jstxt)
    return jsbd


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
	#构造请求头
    headers = {
                     'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                     'Connection':'keep-alive',
                     'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
              } 
    r = requests.get(url,headers = headers)
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

def DownHtmlMain(jsonDir,saveHtmlDir):
    saveHtmlDir = jsbd["htmlDir"]
    if not os.path.exists(saveHtmlDir):
        os.makedirs(saveHtmlDir)
    saveImgDir = os.path.join(saveHtmlDir, "images")
    if not os.path.exists(saveImgDir):
        os.makedirs(saveImgDir)
    ArtList = GetArticleList(jsonDir)
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

#把一个文件夹下的html文件都转为pdf
def PDFDir(htmldir,pdfdir):
    if not os.path.exists(pdfdir):
        os.makedirs(pdfdir)
    flist = os.listdir(htmldir)
    for f in flist:
        if (not f[-5:]==".html") or ("tmp" in f): #不是html文件的不转换，含有tmp的不转换
            continue
        htmlpath = os.path.join(htmldir,f)
        tmppath = htmlpath[:-5] + "_tmp.html"#生成临时文件，供转pdf用
        htmlstr = ReadFile(htmlpath)
        bs = BeautifulSoup(htmlstr, "lxml")
        title = ""
        # pdf文件名中包含文章标题，但如果标题中有不能出现在文件名中的符号则会转换失败
        titleTag = bs.find(id="activity-name")
        if titleTag is not None:
            title = "_" + titleTag.get_text().replace(" ", "").replace("  ","").replace("\n","")
        ridx = htmlpath.rindex("/") + 1
        htmlname = htmlpath[ridx:-5] + title
        pdfpath = os.path.join(pdfdir, htmlname + ".pdf")

        """
            把js等去掉，减少转PDF时的加载项，
            注意此处去掉了css(link），如果发现pdf格式乱了可以不去掉css
        """
        [s.extract() for s in bs(["script", "iframe", "link"])]
        SaveFile(tmppath, str(bs))
        PDFOne(tmppath,pdfpath)

#把一个Html文件转为pdf
def PDFOne(htmlpath,pdfpath,skipExists=True,removehtml=True):
    if skipExists and os.path.exists(pdfpath):
        print("pdf exists",pdfpath)
        if removehtml:
            os.remove(htmlpath)
        return
    exepath = "wkhtmltopdf.exe"#把wkhtmltopdf.exe文件保存到与本py文件相同的目录下
    cmdlist =[]
    cmdlist.append(" --load-error-handling ignore ")
    cmdlist.append(" --page-height 200 ") #数字可以自己调节，也可以不加这两行
    cmdlist.append(" --page-width 140 ")
    cmdlist.append(" " + htmlpath +" ")
    cmdlist.append(" " + pdfpath + " ")
    cmdstr = exepath + "".join(cmdlist)
    print(cmdstr)
    result = subprocess.check_call(cmdstr, shell=False)
    # stdout,stderr = result.communicate()
    # result.wait() #等待转换完一个再转下一个
    if removehtml:
        os.remove(htmlpath)

    """
            先去config.json文件设置
            jsonDir：Fiddler生成的文件
            htmlDir：保存html的目录，路径中不能有空格
            pdfDir：保存pdf的目录，路径中不能有空格
    """


if __name__ == "__main__":
    if len(sys.argv)==1:
        arg = None
    else:
        arg = sys.argv[1]
    if arg is None or arg == "html" :
        jsbd = GetJson()
        saveHtmlDir = jsbd["htmlDir"]
        jsdir= jsbd["jsonDir"]
        DownHtmlMain(jsdir,saveHtmlDir)
    elif arg == "pdf":
        jsbd = GetJson()
        saveHtmlDir = jsbd["htmlDir"]
        savePdfDir = jsbd["pdfDir"]
        PDFDir(saveHtmlDir,savePdfDir)
