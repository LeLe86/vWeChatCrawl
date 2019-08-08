# vWeChatCrawl-小V公众号文章下载(开源版)
批量导出任意微信公众号历史文章，稍有python基础的人都能搞定。  



QQ交流群 703431832 ,加群暗号"不止技术流"  

# 使用步骤：  
## a.安装Python
通过 pip install requirements.txt 安装本项目需要的库。  
## b.安装并配置Fiddler  
Fiddler的官网有时会连不上，可去pc.qq.com搜索Fiddler4  并安装  
![avatar](http://www.xiaokuake.com/p/wp-content/uploads/2019/08/2019080602070412.png)  

会弹出几个窗口，都点 Yes  

![avatar](http://www.xiaokuake.com/p/wp-content/uploads/2019/08/2019080602072832.png)  

最后是这样的，打了 3 个钩。点 OK 保存即可。  

![avatar](http://www.xiaokuake.com/p/wp-content/uploads/2019/08/2019080602075168.png)  

在主窗口右侧按下图所示设置

![avatar](http://www.xiaokuake.com/p/wp-content/uploads/2019/08/201908060209546.png)  

其中需要填的网址为 mp.weixin.qq.com/mp/profile_ext?action=getms  

至此配置完成了，点软件左下角的方块，会显示Capturing ，表示它此时处在可以抓取数据的状态，再点一下会暂停抓取。此处先打开为抓取状态
![avatar](http://www.xiaokuake.com/p/wp-content/uploads/2019/08/2019080602082132.png)  

## c.打开某个微信公众号的历史文章列表
![avatar](http://www.xiaokuake.com/p/wp-content/uploads/2019/08/2019080602060364.png) 

不断下划，使历史文章列表都显示出来，但注意不要划得太快。  

看Fiddler中显示了我们需要的请求  

![avatar](http://www.xiaokuake.com/p/wp-content/uploads/2019/08/2019080602101979.png) 

把这些请求保存下来  

![avatar](http://www.xiaokuake.com/p/wp-content/uploads/2019/08/2019080602105916.png) 
![avatar](https://www.xiaokuake.com/p/wp-content/uploads/2019/08/2019080602105929.png) 

## d.运行python文件
打开本项目的config.json文件，设置  
- jsonDir：Fiddler生成的文件  
- htmlDir：保存html的目录，路径中不能有空格  
- pdfDir：保存pdf的目录，路径中不能有空格  
记得保存  
wkhtmltopdf.exe文件是html转pdf用的，位置不要动。  


运行 python start.py      #开始下载html  
运行 python start.py pdf  #把下载的html转pdf  


## 补充

企业想直接付费使用全功能版及其他公众号相关功能定制的可直达 [https://www.xiaokuake.com](https://www.xiaokuake.com) 或添加作者微信 kakaLongcn

本开源项目仅用于技术学习交流，请勿用于非法用途，由此引起的后果本作者概不负责。


主要思路参考这几篇文章  
[一步步教你打造文章爬虫(1)-综述](https://mp.weixin.qq.com/s?__biz=MzAxMDM4MTA2MA==&mid=2455304602&idx=1&sn=4beadc781c44c17cb4451b579d077c45&chksm=8cfd6bf1bb8ae2e7d5a9f1a66696dd12e260ac7919c7bebe317af81e90bd25591ba286da1f0f&token=2137480545&lang=zh_CN#rd)  
[一步步教你打造文章爬虫(2)-下载网页](https://mp.weixin.qq.com/s?__biz=MzAxMDM4MTA2MA==&mid=2455304609&idx=1&sn=b7496563aab42e92060bd68936bc4212&chksm=8cfd6bcabb8ae2dc606b060fecf3f837177e3ef22a05a30ee28ebefd75c6677b29df3e426692&token=2137480545&lang=zh_CN#rd)  
特别要仔细看第3篇  
[一步步教你打造文章爬虫(3)-批量下载
](https://mp.weixin.qq.com/s?__biz=MzAxMDM4MTA2MA==&mid=2455304632&idx=1&sn=d0a1f6ef7e5d4356d17219a2b79f65d4&chksm=8cfd6bd3bb8ae2c532f901e11aa4b080c19f16626f0dceb291fcb8270e2d7689d7b97d232683&token=2137480545&lang=zh_CN#rd)  

