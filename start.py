import os,sys
import requests
import json
import subprocess
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from time import sleep
from loguru import logger#导入logger


"""
本项目开源地址 https://github.com/LeLe86/vWeChatCrawl
讨论QQ群 703431832

"""
#使用loguru来抓取log相关信息，方便后续修改
#loguru project：https://github.com/Delgan/loguru
logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")
logger.add('log.log')


@logger.catch
#保存文件
def SaveFile(fpath,fileContent):
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(fileContent)

@logger.catch        
#读取文件
def ReadFile(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        all_the_text = f.read()
    return all_the_text

@logger.catch
#时间戳转日期
def Timestamp2Datetime(stampstr):
    dt = datetime.utcfromtimestamp(stampstr)
    dt = dt + timedelta(hours=8)
    newtimestr = dt.strftime("%Y%m%d_%H%M%S")
    return newtimestr

@logger.catch
#初始化环境
def GetJson():
    jstxt = ReadFile("config.json")
    jstxt = jstxt.replace("\\\\","/").replace("\\","/") #防止json中有 / 导致无法识别
    jsbd = json.loads(jstxt)
    if jsbd["htmlDir"][-1]=="/":
        jsbd["htmlDir"] = jsbd["htmlDir"][:-1] 
    if jsbd["jsonDir"][-1]=="/":
        jsbd["jsonDir"]= jsbd["jsonDir"][:-1] 
    return jsbd


@logger.catch
#下载url网页
def DownLoadHtml(url):
    #构造请求头
    headers = {
                     'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                     'Connection':'keep-alive',
                     'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
              } 
    requests.packages.urllib3.disable_warnings()
    
    #使用try……except抓取错误并跳过，避免中断
    try:
        response = requests.get(url,headers = headers,proxies=None,verify=False)
        if response.status_code == 200:
            htmltxt = response.text #返回的网页正文
            return htmltxt
        else:
            return None
    except Exception as e:
        print("\n出现错误，错误如下："+str(e))
        print("----------------------跳过--------------------")
        pass

@logger.catch
#将图片从远程下载保存到本地
def DownImg(url,savepath):
	#构造请求头
    headers = {
                     'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                     'Connection':'keep-alive',
                     'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
              } 
    requests.packages.urllib3.disable_warnings()
    
    
    #使用try……except抓取错误并跳过，避免中断
    try:
        r = requests.get(url,headers = headers,proxies=None,verify=False)
        with open(savepath, 'wb') as f:
            f.write(r.content)
    except Exception as e:
        print("\n出现错误，错误如下："+str(e))
        print("----------------------跳过--------------------")
        pass

@logger.catch
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
            print("\r down imgs " + "▇" * imgindex +" " + str(imgindex),end="")
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
    ChangeContent(bs) #修改js_content的style，使正文能正常显示
    
    #try……except抓取错误并跳过，避免中断
    try:        
        #bs转为str过程中容易出现问题，暂未研究治本方法
        return str(bs) #将BeautifulSoup对象再转换为字符串，用于保存
        
    #出现错误maximum recursion depth exceeded while calling a Python object
    except Exception as e:     
        print("\n出现错误，错误如下："+str(e))
        error="maximum recursion depth exceeded while calling a Python object"
        if str(e)==error:
           maximum_value = int(sys.getrecursionlimit())
           sys.setrecursionlimit(2*maximum_value)#最大深度乘以2
           print("最大递归深度已调整为："+str(2*maximum_value))
        return str(bs)
        

@logger.catch        
def ChangeCssSrc(bs):
    linkList = bs.findAll("link")
    for link in linkList:
        href = link.attrs["href"]
        if href.startswith("//"):
            newhref = "http:" + href
            link.attrs["href"] = newhref

@logger.catch            
def ChangeContent(bs):
    jscontent = bs.find(id="js_content")
    if jscontent:
        jscontent.attrs["style"]=""
    else:
        print("-----可能文章被删了-----")
    
#文章类
class Article():
    def __init__(self,url,pubdate,idx,title):
        self.url = url
        self.pubdate = pubdate
        self.idx = idx
        self.title = title

@logger.catch
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
            
            pubstamp = comm_msg_info["datetime"]
            pubdate = Timestamp2Datetime(pubstamp)
            if comm_msg_info["type"] == 49: #49为普通图文类型，还有其他类型，暂不考虑
                app_msg_ext_info = item["app_msg_ext_info"]
                url = app_msg_ext_info["content_url"] #文章链接
                idx = artidx
                title = app_msg_ext_info["title"]
                art = Article(url,pubdate,idx,title)
                if len(url)>3:#url不完整则跳过
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
                      if len(url)>3:
                        ArtList.append(art)
                      print(len(ArtList),pubdate, idx, title)
    return ArtList


@logger.catch
def DownHtmlMain(jsonDir,saveHtmlDir):
    saveHtmlDir = jsbd["htmlDir"]
    if not os.path.exists(saveHtmlDir):
        os.makedirs(saveHtmlDir)
    saveImgDir = saveHtmlDir+ "/images"
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
        arthtmlsavepath = saveHtmlDir+"/"+arthtmlname
        print(idx,"of",totalCount,artname,art.title)
        # 如果已经有了则跳过，便于暂停后续传
        if os.path.exists(arthtmlsavepath):
            print("exists",arthtmlsavepath)
            continue
            
        arthtmlstr = DownLoadHtml(art.url)

        
        arthtmlstr = ChangeImgSrc(arthtmlstr,saveImgDir,artname)
        print("\r",end="")
        SaveFile(arthtmlsavepath,arthtmlstr)
        sleep(3) #防止下载过快被微信屏蔽，间隔3秒下载一篇

@logger.catch
#把一个文件夹下的html文件都转为pdf
def PDFDir(htmldir,pdfdir):
    if not os.path.exists(pdfdir):
        os.makedirs(pdfdir)
    flist = os.listdir(htmldir)
    for f in flist:
        if (not f[-5:]==".html") or ("tmp" in f): #不是html文件的不转换，含有tmp的不转换
            continue
        htmlpath = htmldir+"/"+f
        tmppath = htmlpath[:-5] + "_tmp.html"#生成临时文件，供转pdf用
        htmlstr = ReadFile(htmlpath)
        bs = BeautifulSoup(htmlstr, "lxml")
        title = ""
        # pdf文件名中包含文章标题，但如果标题中有不能出现在文件名中的符号则会转换失败
        titleTag = bs.find(id="activity-name")
        if titleTag is not None:
            title = "_" + titleTag.get_text().replace(" ", "").replace("  ","").replace("\n","")
        ridx = htmlpath.rindex("/") + 1
        pdfname = htmlpath[ridx:-5] + title
        pdfpath = pdfdir+"/"+ pdfname + ".pdf"

        """
            把js等去掉，减少转PDF时的加载项，
            注意此处去掉了css(link），如果发现pdf格式乱了可以不去掉css
        """
        [s.extract() for s in bs(["script", "iframe", "link"])]
        
        #try……except抓取错误并跳过，避免中断
        try:        
            SaveFile(tmppath, str(bs)) #bs转为str容易出现递归深度问题
            
        #出现错误maximum recursion depth exceeded while calling a Python object
        except Exception as e:     
            print("\n出现错误，错误如下："+str(e))
            error="maximum recursion depth exceeded while calling a Python object"
            if str(e)==error:
               maximum_value = int(sys.getrecursionlimit())
               sys.setrecursionlimit(2*maximum_value)#最大递归深度乘以2
               print("最大递归深度已调整为："+str(2*maximum_value))
            SaveFile(tmppath, str(bs))        
        #SaveFile(tmppath, str(bs))
        PDFOne(tmppath,pdfpath)

@logger.catch
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
    
    
    #执行中出现错误subprocess.CalledProcessError: Command 'wkhtmltopdf.exe
    #错误导致退出：Exit with code 1 due to network error: UnknownNetworkError
    try:
        result = subprocess.check_call(cmdstr, shell=False)
        # stdout,stderr = result.communicate()
        # result.wait() #等待转换完一个再转下一个
        if removehtml:
            os.remove(htmlpath)
    except Exception as e:
        print("\n出现错误，错误如下："+str(e))
        print("----------------------跳过--------------------")
        pass


    """
        1.设置：
            先去config.json文件中设置
            jsonDir：Fiddler生成的文件
            htmlDir：保存html的目录，路径中不能有空格
            pdfDir：保存pdf的目录，路径中不能有空格
        2.使用方法：    
            运行 python start.py      #开始下载html  
            运行 python start.py pdf  #把下载的html转pdf 
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
