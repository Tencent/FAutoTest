# coding=utf-8
from fastAutoTest.core.wx.wxEngine import WxDriver
import os

# 进入企鹅医典小程序
if __name__ == '__main__':
    wxDriver = WxDriver()
    wxDriver.initDriver()
    # 点击全部疾病
    wxDriver.clickElementByXpath('/html/body/div[1]/div/div[3]/p')
    wxDriver.clickFirstElementByText('白内障')
    wxDriver.returnLastPage()
    wxDriver.returnLastPage()
    # 截图
    dirPath = os.path.split(os.path.realpath(__file__))[0]
    PIC_SRC = os.path.join(dirPath, 'pic.png')
    wxDriver.d.screenshot(PIC_SRC)
    wxDriver.close()
