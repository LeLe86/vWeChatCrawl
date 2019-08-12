import pip
from subprocess import call


#如果从默认源安装比较慢的话直接运行这个文件安装
lst=["beautifulsoup4","lxml","requests"]
for pkg in lst:
    call("pip install -i https://pypi.douban.com/simple --upgrade " + pkg)