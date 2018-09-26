# coding=utf-8
from fastAutoTest.core.qq.qqEngine import QQDriver

# 从动态 -> 动漫进入
if __name__ == '__main__':
    qqDriver = QQDriver()
    qqDriver.initDriver()
    qqDriver.clickFirstElementByText('英雄救美，这也太浪漫了')
    qqDriver.returnLastPage()
    qqDriver.clickElementByXpath('//*[@id="app"]/div/ul/li[2]')
    qqDriver.returnLastPage()
    qqDriver.close()
