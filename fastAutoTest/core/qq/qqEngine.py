# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
import sys
import time

import uiautomator
from lxml import etree

from fastAutoTest.core.common.errormsgmanager import ErrorMsgManager, ERROR_CODE_DEVICE_NOT_CONNECT, \
    ERROR_CODE_MULTIPLE_DEVICE
from fastAutoTest.core.common.network.shortLiveWebSocket import ShortLiveWebSocket
from fastAutoTest.core.common.network.websocketdatatransfer import WebSocketDataTransfer
from fastAutoTest.core.h5.h5PageOperator import H5PageOperator
from fastAutoTest.utils import commandHelper
from fastAutoTest.utils import constant
from fastAutoTest.utils.adbHelper import AdbHelper
from fastAutoTest.utils.constant import WAIT_REFLESH_3_SECOND, WAIT_REFLESH_05_SECOND, \
    WAIT_REFLESH_1_SECOND
from fastAutoTest.utils.logger import Log
from fastAutoTest.utils.singlethreadexecutor import SingleThreadExecutor
from fastAutoTest.utils.vmhook import VMShutDownHandler, UncaughtExceptionHandler
from qqWebSocketDebugUrlFetcher import QQWebSocketDebugUrlFetcher

reload(sys)
sys.setdefaultencoding('utf8')
__all__ = {
    "QQDriver"
}


class QQDriver(object):
    def initDriver(self):
        if self._hasInit:
            return

        self._urlFetcher = QQWebSocketDebugUrlFetcher(device=self._device)
        url = self._urlFetcher.fetchWebSocketDebugUrl()
        self._vmShutdownHandler.registerToVM()
        UncaughtExceptionHandler.init()
        UncaughtExceptionHandler.registerUncaughtExceptionCallback(self._onUncaughtException)

        self._selectDevice()

        self._webSocketDataTransfer = WebSocketDataTransfer(url=url)
        self._networkHandler = ShortLiveWebSocket(self._webSocketDataTransfer, self._executor, self)
        self._networkHandler.connect()
        self._executor.put(self._networkHandler.receive)

        self.initPageDisplayData()
        self.logger = Log().getLogger()
        self._hasInit = True

    def __init__(self, device=None):
        self._device = device
        self._urlFetcher = None
        self._webSocketDataTransfer = None
        self._vmShutdownHandler = VMShutDownHandler()
        self._networkHandler = None
        self._executor = SingleThreadExecutor()

        self._pageOperator = H5PageOperator()

        self._hasInit = False

        self.d = uiautomator.Device(self._device)
        self.html = None

    def getDriverType(self):
        return constant.QQDRIVER

    def initPageDisplayData(self):
        driverInfo = self.d.info
        displayDp = driverInfo.get('displaySizeDpY')
        displayPx = driverInfo.get('displayHeight')
        self.scale = (displayPx - 0.5) / displayDp
        windowHeight = self.getWindowHeight()
        self.appTitleHeight = displayDp - windowHeight

    def changeDp2Px(self, xDp, yDp):
        xPx, yPx = self._pageOperator.changeDp2Px(xDp, yDp, self.scale, self.appTitleHeight)
        return xPx, yPx

    def needSwitchNextPage(self):
        return self._urlFetcher.needSwitchNextPage()

    def _selectDevice(self):
        devicesList = AdbHelper.listDevices(ignoreUnconnectedDevices=True)
        # 假如没有指定设备，那么判断当前机器是否连接1个设备
        if self._device is None:
            devicesCount = len(devicesList)
            errorMsg = None

            if devicesCount <= 0:
                errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_DEVICE_NOT_CONNECT)

            elif devicesCount == 1:
                self._device = devicesList[0]

            else:
                errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_MULTIPLE_DEVICE)

            if errorMsg is not None:
                raise RuntimeError(errorMsg)

    def switchToNextPage(self):
        """
        需要重新获取当前页面的websocket的url
        """
        self._networkHandler.disconnect()
        url = self._urlFetcher.fetchWebSocketDebugUrl(refetch=True)
        self.logger.debug('url -> ' + url)
        self._webSocketDataTransfer.setUrl(url)
        self._networkHandler.connect()
        self.wait(WAIT_REFLESH_05_SECOND)

    def returnLastPage(self):
        self.logger.info('')
        self.wait(WAIT_REFLESH_1_SECOND)
        self._networkHandler.disconnect()
        self.switchToNextPage()
        self._networkHandler.disconnect()
        self.d.press('back')
        self.wait(WAIT_REFLESH_1_SECOND)
        self.switchToNextPage()

    def getDocument(self):
        """
        获得getHtml中需要的nodeId
        在调用getHtml之前必须先调用这个方法
        """
        sendStr = self._pageOperator.getDocument()
        return self._networkHandler.send(sendStr)

    def getHtml(self, nodeId=1):
        """
        获得指定nodeId的Html代码。在一条websocket连接中，方法只能够执行一次。
        :param nodeId: getDocument方法返回的nodeId，当为1时，返回整个body的代码
        """
        self.logger.info('')
        self.switchToNextPage()
        self.getDocument()
        sendStr = self._pageOperator.getHtml(nodeId)
        self.html = self._networkHandler.send(sendStr).getResponse()[0]['result']['outerHTML']
        return self.html

    def isElementExist(self, xpath):
        self.logger.info('xpath ---> ' + xpath)
        getExistCmd = self._pageOperator.isElementExist(xpath)
        resultValueDict = self._networkHandler.send(getExistCmd).getResponse()[0]
        resultType = resultValueDict['result']['result']['subtype']
        if resultType == 'null':
            self.wait(WAIT_REFLESH_3_SECOND)
            self.switchToNextPage()
            getExistCmd = self._pageOperator.isElementExist(xpath)
            resultValueDict = self._networkHandler.send(getExistCmd).getResponse()[0]
            resultType = resultValueDict['result']['result']['subtype']
        self.logger.debug('isElementExist Response --> ' + str(resultValueDict))
        return resultType != 'null'

    def getElementTextByXpath(self, xpath):
        time.sleep(WAIT_REFLESH_1_SECOND)
        self.logger.info('xpath ---> ' + xpath)
        self.switchToNextPage()
        if self.isElementExist(xpath):
            getTextCmd = self._pageOperator.getElementTextByXpath(xpath)
            resultValueDict = self._networkHandler.send(getTextCmd).getResponse()[0]
            resultValue = resultValueDict['result']['result']['value'].encode("utf-8")
        else:
            resultValue = None
        return resultValue

    def getElementSrcByXpath(self, xpath):
        time.sleep(WAIT_REFLESH_1_SECOND)
        self.logger.info('xpath ---> ' + xpath)
        self.switchToNextPage()
        if self.isElementExist(xpath):
            getSrcCmd = self._pageOperator.getElementSrcByXpath(xpath)
            resultValueDict = self._networkHandler.send(getSrcCmd).getResponse()[0]
            resultValue = resultValueDict['result']['result']['value'].encode("utf-8")
        else:
            resultValue = None
        return resultValue

    def getElementByXpath(self, xpath):
        """
        :param:目标的xpath
        :return:返回lxml包装过的element对象，可以使用lxml语法获得对象的信息
        例如：可以使用element.get("attrs")来拿到属性的数据
        可以用element.text拿到它的文字
        当element中含有列表时，使用for循环读取每一个item
        """
        time.sleep(WAIT_REFLESH_1_SECOND)
        self.logger.info('xpath ---> ' + xpath)
        htmlData = self.getHtml()
        if htmlData is not None:
            html = etree.HTML(htmlData)
            elementList = html.xpath(xpath)
            if len(elementList) != 0:
                return elementList[0]
            else:
                self.logger.info('找不到xpath为: ' + xpath + ' 的控件')
                return ''
        else:
            self.logger.info('获取到的html为空')
            return ''

    def textElementByXpath(self, xpath, text):
        """
               先获取输入框的焦点, 再使用Chrome debug协议的输入api,再输入文字内容
               :param xpath:输入框的xpath
               :parm text:要输入的文字
               """
        self.logger.info('xpath ---> ' + xpath + ' text ---> ' + text)
        self.focusElementByXpath(xpath)
        sendStrList = self._pageOperator.textElementByXpath(text)

        for command in sendStrList:
            self._networkHandler.send(command)
        self.wait(WAIT_REFLESH_05_SECOND)

    def clickElementByXpath(self, xpath, visibleItemXpath=None, byUiAutomator=False):
        """
        默认滑动点为屏幕的中心，且边距为整个屏幕。当有container时，传入container中任意一个当前可见item的xpath，之后会将目标滑到该可见item的位置
        :param xpath: 要滑动到屏幕中控件的xpath
        :param visibleItemXpath: container中当前可见的一个xpath
        :return:
        """
        self.logger.info('xpath ---> ' + xpath)
        self.scrollToElementByXpath(xpath, visibleItemXpath)

        sendStr = self._pageOperator.getElementRect(xpath)
        self._networkHandler.send(sendStr)

        x = self._getRelativeDirectionValue('x')
        y = self._getRelativeDirectionValue('y')
        self.logger.debug('clickElementByXpath x:' + str(x) + '  y:' + str(y))

        if not byUiAutomator:
            clickCommand = self._pageOperator.clickElementByXpath(x, y)
            return self._networkHandler.send(clickCommand)
        else:
            xPx, yPx = self.changeDp2Px(x, y)
            self.d.click(xPx, yPx)

    def clickFirstElementByText(self, text, visibleItemXpath=None, byUiAutomator=False):
        """
        通过text来搜索，点击第一个text相符合的控件。参数同clickElementByXpath()
        """
        self.clickElementByXpath('.//*[text()="' + text + '"]', visibleItemXpath, byUiAutomator)

    def focusElementByXpath(self, xpath):
        """
        调用目标的focus()方法。
        :param xpath:目标的xpath
        """
        executeCmd = self._pageOperator.focusElementByXpath(xpath)
        self._networkHandler.send(executeCmd)

    def getElementCoordinateByXpath(self, elementXpath):
        '''
        获得Element的坐标
        :param elementXpath:待获取坐标的元素的xpath
        :return:element相对于整个屏幕的x、y坐标，单位为px
        '''
        self.logger.info(
            'elementXpathXpath ---> ' + elementXpath)

        sendStr = self._pageOperator.getElementRect(elementXpath)
        self._networkHandler.send(sendStr)
        x = self._getRelativeDirectionValue('x')
        y = self._getRelativeDirectionValue('y')
        xPx, yPx = self.changeDp2Px(x, y)
        return xPx, yPx

    def scrollToElementByXpath(self, xpath, visibleItemXpath=None, speed=600):
        """
        默认滑动点为屏幕的中心，且边距为整个屏幕。当有container时，传入container中任意一个当前可见item的xpath，之后会将目标滑到该可见item的位置
        :param xpath: 要滑动到屏幕中控件的xpath
        :param visibleItemXpath: container中当前可见的一个xpath
        :return:
        """
        self.logger.info('xpath ---> ' + xpath)
        sendStr = self._pageOperator.getElementRect(xpath)
        self._networkHandler.send(sendStr)

        top = self._getRelativeDirectionValue('topp')
        bottom = self._getRelativeDirectionValue('bottom')
        left = self._getRelativeDirectionValue('left')
        right = self._getRelativeDirectionValue('right')
        self.logger.debug('scrollToElementByXpath -> top:bottom:left:right = ' + str(top) + " :" + str(bottom) \
                          + " :" + str(left) + " :" + str(right))

        if visibleItemXpath is None:
            endTop = 0
            endLeft = 0
            endBottom = self.getWindowHeight()
            endRight = self.getWindowWidth()
        else:
            sendStr = self._pageOperator.getElementRect(visibleItemXpath)
            self._networkHandler.send(sendStr)

            endTop = self._getRelativeDirectionValue('topp')
            endBottom = self._getRelativeDirectionValue('bottom')
            endLeft = self._getRelativeDirectionValue('left')
            endRight = self._getRelativeDirectionValue('right')
            self.logger.debug(
                'scrollToElementByXpath -> toendTop:endBottom:endLeft:endRight = ' + str(endTop) + " :" + str(
                    endBottom) \
                + " :" + str(endLeft) + " :" + str(endRight))

        '''
        竖直方向的滑动
        '''
        if endBottom < bottom:
            scrollYDistance = endBottom - bottom
        elif top < 0:
            scrollYDistance = -(top - endTop)
        else:
            scrollYDistance = 0

        if scrollYDistance != 0:
            self.scrollWindow(int((endLeft + endRight) / 2), int((endTop + endBottom) / 2), 0, scrollYDistance,
                              speed)
        else:
            self.logger.debug('y方向不需要滑动')
        '''
        水平方向的滑动
        '''
        if right > endRight:
            scrollXDistance = endRight - right
        elif left < 0:
            scrollXDistance = -(left - endLeft)
        else:
            scrollXDistance = 0

        if scrollXDistance != 0:
            self.scrollWindow(int((endLeft + endRight) / 2), int((endTop + endBottom) / 2), scrollXDistance, 0,
                              speed)
        else:
            self.logger.debug('x方向不需要滑动')

    def scrollWindow(self, x, y, xDistance, yDistance, speed=800):
        self.logger.info('')
        sendStr = self._pageOperator.scrollWindow(x, y, xDistance, yDistance, speed)
        return self._networkHandler.send(sendStr)

    def _getRelativeDirectionValue(self, directionKey='topp'):
        '''
        获取相关的方向数据参数值
        :param directionKey: key值
        :return:
        '''
        directionCommand = self._pageOperator.getJSValue(directionKey)
        directionResponse = self._networkHandler.send(directionCommand).getResponse()[0]
        directionValue = directionResponse['result']['result']['value']
        return directionValue

    '''
    性能数据
    '''

    def getMemoryInfo(self):
        '''
        获得小程序进程占用内存信息
        :return: 小程序进程占用内存信息
        '''
        self.logger.info('')
        ADB_SHELL = 'adb shell '
        if self._device:
            ADB_SHELL = ADB_SHELL.replace("adb", "adb -s %s" % self._device)
        GET_MEMORY_INFO = ADB_SHELL + 'dumpsys meminfo com.tencent.mm:appbrand0'
        return commandHelper.runCommand(GET_MEMORY_INFO)

    def getCPUInfo(self):
        '''
        获得小程序进程占用CPU信息
        :return: 小程序进程占用CPU信息
        '''
        self.logger.info('')
        ADB_SHELL = 'adb shell '
        if self._device:
            ADB_SHELL = ADB_SHELL.replace("adb", "adb -s %s" % self._device)
        GET_CPU_INFO = ADB_SHELL + ' top -n 1 | grep com.tencent.mm:appbrand0'
        return commandHelper.runCommand(GET_CPU_INFO)

    def getPageHeight(self):
        getPageHeightCmd = self._pageOperator.getPageHeight()
        resultValueDict = self._networkHandler.send(getPageHeightCmd).getResponse()[0]
        resultValue = resultValueDict['result']['result']['value']
        return resultValue

    def getWindowWidth(self):
        '''
        :return:手机屏幕的宽度
        '''
        getWindowWidthCmd = self._pageOperator.getWindowWidth()
        resultValueDict = self._networkHandler.send(getWindowWidthCmd).getResponse()[0]
        resultValue = resultValueDict['result']['result']['value']
        return resultValue

    def getWindowHeight(self):
        '''
        :return:手机屏幕的高度
        '''
        getWindowHeightCmd = self._pageOperator.getWindowHeight()
        resultValueDict = self._networkHandler.send(getWindowHeightCmd).getResponse()[0]
        resultValue = resultValueDict['result']['result']['value']
        return resultValue

    def wait(self, seconds):
        time.sleep(seconds)

    def addShutDownHook(self, func, *args, **kwargs):
        '''
        添加当程序正常关闭时的操作,可以进行一些环境清理操作等
        '''
        self._vmShutdownHandler.registerVMShutDownCallback(func, *args, **kwargs)

    def _onUncaughtException(self, exctype, value, tb):
        self.close()

    def close(self):
        if self._networkHandler is not None:
            self._networkHandler.quit()

        if self._executor is not None:
            self._executor.shutDown()

        UncaughtExceptionHandler.removeHook()

    def setDebugLogMode(self):
        '''
        开启debug的日志模式
        '''
        Log().setDebugLogMode()


if __name__ == "__main__":
    pass
