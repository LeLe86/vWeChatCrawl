from PIL import Image

def GenFaceFlag(mainPicPath,flagPath,savepath):
    mainImg = Image.open(mainPicPath) #主图
    flagImg = Image.open(flagPath) #要添加的小旗
    mw,mh = mainImg.size
    fw,fh = flagImg.size
    if fw>(int)(mw * 0.3):#如果flag的尺寸太大则要缩放
        newwidth = (int)(mw*0.3)
        newheight = (int)(mw*0.3*fh/fw)
        flagImgNew=flagImg.resize((newwidth,newheight))
    else:
        newwidth = fw
        newheight =fh
        flagImgNew = flagImg
    lt_x=mw-newwidth#计算要把flag粘贴的位置
    lt_y=mh-newheight
    mainImg.paste(flagImgNew,(lt_x,lt_y)) #粘贴
    mainImg.save(savepath)#保存新图像

if __name__=="__main__":
    mainpath = "C:\\Python\\vWXCrawl\\pub\\vWeChatCrawl\\main2.jpg"
    flagpath = "C:\\Python\\vWXCrawl\\pub\\vWeChatCrawl\\flag2.png"
    savepath = "C:\\Python\\vWXCrawl\\pub\\vWeChatCrawl\\save.png"

    GenFaceFlag(mainpath,flagpath,savepath)