# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
import time
import uiautomator
import fastAutoTest.utils.commandHelper as commandHelper

from lxml import etree

from fastAutoTest.core.common.network.shortLiveWebSocket import ShortLiveWebSocket
from fastAutoTest.core.common.network.websocketdatatransfer import WebSocketDataTransfer

from fastAutoTest.core.h5.h5WebSocketDebugUrlFetcher import H5WebSocketDebugUrlFetcher

from fastAutoTest.core.common.errormsgmanager import ErrorMsgManager, ERROR_CODE_DEVICE_NOT_CONNECT, \
    ERROR_CODE_MULTIPLE_DEVICE, ERROR_CODE_GETCOORDINATE, ERROR_CODE_SETUP_FRAME_PAGE

from fastAutoTest.utils.adbHelper import AdbHelper
from fastAutoTest.utils.constant import WAIT_REFLESH_05_SECOND, WAIT_REFLESH_2_SECOND, H5DRIVER

from fastAutoTest.utils.singlethreadexecutor import SingleThreadExecutor

from fastAutoTest.core.h5.h5PageOperator import H5PageOperator

from fastAutoTest.utils.vmhook import VMShutDownHandler, UncaughtExceptionHandler
from fastAutoTest.utils import constant
from fastAutoTest.utils.logger import Log

import sys

reload(sys)
sys.setdefaultencoding('utf8')

__all__ = [
    "H5Driver"
]


class H5Driver(object):
    def __init__(self, device=None):
        self._device = device
        self._urlFetcher = None
        self._webSocketDataTransfer = None
        self._vmShutdownHandler = VMShutDownHandler()
        self._networkHandler = None

        self._pageOperator = H5PageOperator()
        self.d = uiautomator.Device(self._device)
        self._hasInit = False

        self.html = None
        self.bodyNode = None

    def initDriver(self):
        if self._hasInit:
            return
        self._executor = SingleThreadExecutor()
        self._vmShutdownHandler.registerToVM()
        UncaughtExceptionHandler.init()
        UncaughtExceptionHandler.registerUncaughtExceptionCallback(self._onUncaughtException)

        self._selectDevice()
        self._urlFetcher = H5WebSocketDebugUrlFetcher(device=self._device)
        url = self._urlFetcher.fetchWebSocketDebugUrl()

        self._webSocketDataTransfer = WebSocketDataTransfer(url=url)
        self._networkHandler = ShortLiveWebSocket(self._webSocketDataTransfer, self._executor, self)
        self._networkHandler.connect()

        self._executor.put(self._networkHandler.receive)
        self.logger = Log().getLogger()
        self.initPageDisplayData()
        self._hasInit = True
        self.logger.info('url ----> ' + url)

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

    def wait(self, seconds=1):
        time.sleep(seconds)

    def _onUncaughtException(self, exctype, value, tb):
        self.close()

    def close(self):
        if self._networkHandler is not None:
            self._networkHandler.quit()

        if self._executor is not None:
            self._executor.shutDown()

        self._hasInit = False

        UncaughtExceptionHandler.removeHook()

    def addShutDownHook(self, func, *args, **kwargs):
        self._vmShutdownHandler.registerVMShutDownCallback(func, *args, **kwargs)

    def getDriverType(self):
        return constant.H5DRIVER

    def switchToNextPage(self):
        """
        把之前缓存的html置为none
        再重新连接websocket
        """
        self.logger.debug('')
        self.html = None
        self._networkHandler.disconnect()
        self._networkHandler.connect()

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

    def clickElementByXpath(self, xpath, visibleItemXpath=None, duration=50, tapCount=1):
        """
        默认滑动点为屏幕的中心，且边距为整个屏幕。当有container时，传入container中任意一个当前可见item的xpath，之后会将目标滑到该可见item的位置
        :param xpath: 要滑动到屏幕中控件的xpath
        :param visibleItemXpath: container中当前可见的一个xpath
        :return:
        """
        self.logger.info('xpath ---> ' + xpath)
        # 防止websocket未失效但页面已经开始跳转
        self.wait(WAIT_REFLESH_05_SECOND)

        if self.isElementExist(xpath):
            self.scrollToElementByXpath(xpath, visibleItemXpath)

            sendStr = self._pageOperator.getElementRect(xpath)
            self._networkHandler.send(sendStr)

            x = self._getRelativeDirectionValue("x")
            y = self._getRelativeDirectionValue("y")

            self.logger.debug('clickElementByXpath --> x:' + str(x) + '   y:' + str(y))
            clickCommand = self._pageOperator.clickElementByXpath(x, y, duration, tapCount)
            return self._networkHandler.send(clickCommand)

    def clickFirstElementByText(self, text, visibleItemXpath=None, duration=50, tapCount=1):
        """
        通过text来搜索，点击第一个text相符合的控件。参数同clickElementByXpath()
        """
        self.clickElementByXpath('.//*[text()="' + text + '"]', visibleItemXpath, duration, tapCount)

    def longClickElementByXpath(self, xpath, visibleItemXpath=None, duration=2000, tapCount=1):
        self.clickElementByXpath(xpath, visibleItemXpath, duration, tapCount)

    def repeatedClickElementByXpath(self, xpath, visibleItemXpath=None, duration=50, tapCount=2):
        self.clickElementByXpath(xpath, visibleItemXpath, duration, tapCount)

    def scrollToElementByXpath(self, xpath, visibleItemXpath=None, speed=400):
        """
        滑动屏幕，使指定xpath的控件可见
        默认滑动点为屏幕的中心，且边距为整个屏幕。当有container时，传入container中任意一个当前可见item的xpath，之后会将目标滑到该可见item的位置
        :param xpath: 要滑动到屏幕中控件的xpath
        :param visibleItemXpath: container中当前可见的一个xpath
        """
        self.logger.info('xpath ---> ' + xpath)
        sendStr = self._pageOperator.getElementRect(xpath)
        self._networkHandler.send(sendStr)
        top = self._getRelativeDirectionValue("topp")
        bottom = self._getRelativeDirectionValue("bottom")
        left = self._getRelativeDirectionValue("left")
        right = self._getRelativeDirectionValue("right")

        if visibleItemXpath is None:
            endTop = 0
            endLeft = 0
            endBottom = self.getWindowHeight()
            endRight = self.getWindowWidth()
        else:
            containerSendStr = self._pageOperator.getElementRect(visibleItemXpath)
            self._networkHandler.send(containerSendStr)

            endTop = self._getRelativeDirectionValue("topp")
            endBottom = self._getRelativeDirectionValue("bottom")
            endLeft = self._getRelativeDirectionValue("left")
            endRight = self._getRelativeDirectionValue("right")

        '''
        竖直方向的滑动
        '''
        if bottom > endBottom:
            scrollYDistance = endBottom - bottom
        elif top < 0:
            scrollYDistance = -(top - endTop)
        else:
            scrollYDistance = 0

        if scrollYDistance < 0:
            self.scrollWindow(int((endLeft + endRight) / 2), int((endTop + endBottom) / 2), 0, scrollYDistance - 80,
                              speed)
        elif scrollYDistance > 0:
            self.scrollWindow(int((endLeft + endRight) / 2), int((endTop + endBottom) / 2), 0, scrollYDistance + 80,
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
            self.logger.debug('y方向不需要滑动')

    def getElementCoordinateByXpath(self, elementXpath):
        '''
        获得Element的坐标
        :param elementXpath:待获取坐标的元素的xpath
        :return:element相对于整个屏幕的x、y坐标，单位为px
        '''
        self.logger.info(
            'elementXpathXpath ---> ' + elementXpath)
        # 防止websocket未失效但页面已经开始跳转
        self.wait(WAIT_REFLESH_05_SECOND)
        if self.isElementExist(elementXpath):
            sendStr = self._pageOperator.getElementRect(elementXpath)
            self._networkHandler.send(sendStr)
            x = self._getRelativeDirectionValue("x")
            y = self._getRelativeDirectionValue("y")
            x, y = self.changeDp2Px(x, y)
            return x, y
        errorMessage = ErrorMsgManager().errorCodeToString(ERROR_CODE_GETCOORDINATE)
        raise RuntimeError(errorMessage)

    def clearInputTextByXpath(self, xpath):
        '''
        清空输入框的文字
        :param xpath:input框的xpath
        '''
        self.logger.info('xpath ---> ' + xpath)
        clearInputTextSendStr = self._pageOperator.clearInputTextByXpath(xpath)
        self._networkHandler.send(clearInputTextSendStr)

    def getWindowHeight(self):
        '''
        :return:手机屏幕的高度
        '''
        getWindowHeightCmd = self._pageOperator.getWindowHeight()
        resultValueDict = self._networkHandler.send(getWindowHeightCmd).getResponse()[0]
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

    def scrollWindow(self, x, y, xDistance, yDistance, speed=800):
        """
        通过坐标来滑动（屏幕的左上角为(0,0),向下和向右坐标逐渐增大）
        :param x: 滑动的起始X点坐标
        :param y: 滑动的起始Y点坐标
        :param xDistance: X方向滑动的距离
        :param yDistance: Y方向滑动的距离
        :param speed: 滑动的速度
        """
        sendStr = self._pageOperator.scrollWindow(x, y, xDistance, yDistance, speed)
        return self._networkHandler.send(sendStr)

    def _getRelativeDirectionValue(self, directionKey='topp', contextId=None):
        '''
        获取相关的方向数据参数值
        :param directionKey: 获取的方向
        :return:
        '''
        directionCommand = self._pageOperator.getJSValue(directionKey, contextId)
        directionResponse = self._networkHandler.send(directionCommand).getResponse()[0]
        directionValue = directionResponse['result']['result']['value']
        return directionValue

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

    def focusElementByXpath(self, xpath):
        """
        调用目标的focus()方法。
        :param xpath:目标的xpath
        """
        executeCmd = self._pageOperator.focusElementByXpath(xpath)
        self._networkHandler.send(executeCmd)

    def getHtml(self, nodeId=1):
        """
        获得指定nodeId的Html代码。在一条websocket连接中，方法只能够执行一次。
        :param nodeId: getDocument方法返回的nodeId，当为1时，返回整个body的代码
        """
        self.logger.info('')
        if self.html is not None:
            self.switchToNextPage()

        self.getDocument()

        sendStr = self._pageOperator.getHtml(nodeId)
        self.html = self._networkHandler.send(sendStr).getResponse()[0]['result']['outerHTML']
        return self.html

    def getDocument(self):
        """
        获得getHtml中需要的nodeId
        在调用getHtml之前必须先调用这个方法
        """
        sendStr = self._pageOperator.getDocument()
        return self._networkHandler.send(sendStr)

    def closeWindow(self):
        """
        关闭整个h5页面
        """
        sendStr = self._pageOperator.closeWindow()
        return self._networkHandler.send(sendStr)

    def returnLastPage(self):
        """
        返回上一页
        """
        self.logger.info('')
        self.wait(WAIT_REFLESH_05_SECOND)
        sendStr = self._pageOperator.returnLastPage()
        self._networkHandler.send(sendStr)
        self.wait(WAIT_REFLESH_05_SECOND)

    def scrollPickerByXpath(self, xpath):
        """
        滑动选择picker的选项
        要获取四个变量，所以发送了四次消息。
        1.先定位到要点击的item
        2.找到它的parent（即整个picker的content区域），并且获得要点击item的index，和总共item的个数
        3.获得picker的BoundingClientRect。再计算每个item的位置，要滑动的距离
        4.因为picker窗口弹出时，默认选择上一次的item，所以先进行一次滑动到顶端。
        （为了避免滑动时的惯性，需要设置一个speed属性，控制速度）
        :param xpath: 要选择的item
        """
        self.logger.info('xpath ---> ' + xpath)

        sendStr = self._pageOperator.getPickerRect(xpath)
        self._networkHandler.send(sendStr)

        startScrollX = self._getRelativeDirectionValue("start_scroll_x")
        startScrollY = self._getRelativeDirectionValue("start_scroll_y")

        # 获取整个列表的高度
        height = self._getRelativeDirectionValue("height")

        # 获取要滑动的距离
        dex = self._getRelativeDirectionValue("dex")

        scrollWindowCmd = self._pageOperator.scrollWindow(startScrollX, startScrollY, startScrollX, height)
        self._networkHandler.send(scrollWindowCmd)

        scrollWIndowWithSpeedCmd = self._pageOperator.scrollWindow(startScrollX, startScrollY, startScrollX, -dex,
                                                                   speed=72)
        self._networkHandler.send(scrollWIndowWithSpeedCmd)

    def getPageHeight(self):
        getPageHeightCmd = self._pageOperator.getPageHeight()
        resultValueDict = self._networkHandler.send(getPageHeightCmd).getResponse()[0]
        resultValue = resultValueDict['result']['result']['value']
        return resultValue

    def getElementTextByXpath(self, xpath):
        '''
        :param xpath: 目标的xpath
        :return: 获取到的目标text内容
        '''
        self.logger.info('xpath ---> ' + xpath)
        if self.isElementExist(xpath):
            getTextCmd = self._pageOperator.getElementTextByXpath(xpath)
            resultValueDict = self._networkHandler.send(getTextCmd).getResponse()[0]
            resultValue = resultValueDict['result']['result']['value'].encode("utf-8")
        else:
            resultValue = None
        return resultValue

    def getElementSrcByXpath(self, xpath):
        """
        :param xpath: 目标的xpath
        :return: 获取到的目标src内容
        """
        self.logger.info('xpath ---> ' + xpath)
        if self.isElementExist(xpath):
            getSrcCmd = self._pageOperator.getElementSrcByXpath(xpath)
            resultValueDict = self._networkHandler.send(getSrcCmd).getResponse()[0]
            resultValue = resultValueDict['result']['result']['value'].encode("utf-8")
        else:
            resultValue = None
        return resultValue

    def getElementClassNameByXpath(self, xpath):
        '''
        :param xpath:目标的xpath
        :return: 目标的className
        '''
        self.logger.info('xpath ---> ' + xpath)
        if self.isElementExist(xpath):
            getClassNameCmd = self._pageOperator.getElementClassNameByXpath(xpath)
            resultValueDict = self._networkHandler.send(getClassNameCmd).getResponse()[0]
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
        self.logger.info('xpath ---> ' + xpath)
        html = etree.HTML(self.getHtml())
        return html.xpath(xpath)[0]

    def isElementExist(self, xpath, contextId=None):
        """
        :param xpath: 目标的xpath
        :return: 返回一个boolean，该Element是否存在
        """
        self.logger.info('xpath ---> ' + xpath)
        getExistCmd = self._pageOperator.isElementExist(xpath, contextId)
        resultValueDict = self._networkHandler.send(getExistCmd).getResponse()[0]
        resultType = resultValueDict['result']['result']['subtype']
        num = 0
        while resultType == 'null' and num < 3:
            self.wait(WAIT_REFLESH_2_SECOND)
            getExistCmd = self._pageOperator.isElementExist(xpath, contextId)
            resultValueDict = self._networkHandler.send(getExistCmd).getResponse()[0]
            resultType = resultValueDict['result']['result']['subtype']
            num = num + 1
        return resultType != 'null'

    def navigateToPage(self, url):
        """
        跳转到指定url，在某些微信版本上不生效
        :param url: 要跳转的url
        """
        self.logger.info('url ---> ' + url)
        navigateCmd = self._pageOperator.navigateToPage(url)
        self._networkHandler.send(navigateCmd)

    def executeScript(self, script):
        """
        手动发送js命令并执行
        :param script:要执行的js指令
        :return: 执行结果
        """
        executeCmd = self._pageOperator.executeScript(script)
        resultValueDict = self._networkHandler.send(executeCmd).getResponse()[0]

        return resultValueDict

    def getCurrentPageUrl(self):
        """
        获得当前页面的url
        :return:
        """
        executeCmd = self._pageOperator.getCurrentPageUrl()
        resultValueDict = self._networkHandler.send(executeCmd).getResponse()[0]
        resultValue = resultValueDict['result']['result']['value'].encode("utf-8")
        return resultValue

    '''
    针对跨域IFrame进行的操作
    '''

    def _getAllNodeId(self):
        '''
        获得body标签中所有的包含IFrame数据的NodeId
        :return:
        '''
        nodeIdList = []
        nodesList = self.getBodyNode()['params']['nodes']
        for node in nodesList:
            if node.get('contentDocument') is not None:
                nodeIdList.append(node.get('contentDocument').get('nodeId'))
        return nodeIdList

    def getBodyNode(self):
        '''
        :return:获得body中所有node的frameId
        '''
        self.switchToNextPage()
        self.wait(WAIT_REFLESH_2_SECOND)
        self.getDocument()
        executeCmd = self._pageOperator.getBodyNode()
        resultValueDict = self._networkHandler.send(executeCmd).getResponse()[0]
        return resultValueDict

    def requestChildNodes(self, nodeId=5):
        '''
        :param nodeId:指定的nodeId
        :return:
        '''
        self.switchToNextPage()
        self.wait(WAIT_REFLESH_2_SECOND)
        self.getDocument()
        executeCmd = self._pageOperator.requestChildNodes(nodeId)
        resultValueDict = self._networkHandler.send(executeCmd).getResponse()[0]
        return resultValueDict

    def getIFrameContextId(self):
        '''
        当body标签中只存在一个IFrame调用
        :return:ContextId
        '''
        time.sleep(5)
        frameIdList = self.getAllIFrameNode()
        contextList = self.getAllContext()
        if len(frameIdList) == 1:
            for contextInfo in contextList:
                if contextInfo["frameId"] == frameIdList[0]:
                    return contextInfo["contextId"]

    def getAllContext(self):
        '''
        获得所有的Context　
        :return: 所有的ContextId，域以及FrameId
        '''
        executeCmd = self._pageOperator.getAllContext()
        resultValueDict = self._networkHandler.send(executeCmd).getResponse()
        resultDictList = []
        for dict in resultValueDict:
            if dict.get('result') is None:
                resultDict = {}
                if dict.get('params').get('context') is not None:
                    context = dict.get('params').get('context')
                    origin = context.get('origin')
                    contextId = context.get('id')
                    frameId = context.get('auxData').get('frameId')
                    resultDict['origin'] = origin
                    resultDict['contextId'] = contextId
                    resultDict['frameId'] = frameId
                    resultDictList.append(resultDict)
        return resultDictList

    def getAllIFrameNode(self):
        '''
        获得body标签中所有的IFrameNode
        :return:
        '''
        try:
            iFrameNodeList = []
            nodesList = self.getBodyNode()['params']['nodes']
            for node in nodesList:
                if node['nodeName'] == 'IFRAME':
                    iFrameNodeList.append(node)
            frameIdList = []
            for iFrameNode in iFrameNodeList:
                frameIdList.append(iFrameNode['frameId'])
            return frameIdList
        except:
            errorMessage = ErrorMsgManager().errorCodeToString(ERROR_CODE_SETUP_FRAME_PAGE)
            raise RuntimeError(errorMessage)

    def getIFrameNodeId(self):
        '''
        当body标签中只存在一个IFrame调用
        :return:IFrame的NodeId，可以通过它获得html
        '''
        nodeIdList = self._getAllNodeId()
        if len(nodeIdList) == 1:
            return nodeIdList[0]

    def getIFrameElementCoordinateByXpath(self, elementXpath, iFrameXpath, contextId):
        '''
        获得IFrame中元素的坐标
        :param elementXpath:待获取坐标的元素的xpath
        :param iFrameXpath: 外层iFrame的xpath
        :param contextId: iFrame的ContextId
        :return:element相对于整个屏幕的x、y坐标，单位为px
        '''
        self.logger.info(
            'elementXpathXpath ---> ' + elementXpath + ' iFrameXpath ---> ' + iFrameXpath + ' contextId ---> ' + str(
                contextId))
        # 防止websocket未失效但页面已经开始跳转
        self.wait(WAIT_REFLESH_05_SECOND)
        if self.isElementExist(iFrameXpath):
            sendStr = self._pageOperator.getElementRect(iFrameXpath)
            self._networkHandler.send(sendStr)
            iframeLeft = self._getRelativeDirectionValue("left")
            iframeTop = self._getRelativeDirectionValue("topp")
            if self.isElementExist(elementXpath, contextId):
                sendStr = self._pageOperator.getElementRect(elementXpath, contextId)
                self._networkHandler.send(sendStr)
                x = self._getRelativeDirectionValue("x", contextId)
                y = self._getRelativeDirectionValue("y", contextId)
                x = iframeLeft + x
                y = iframeTop + y
                x, y = self.changeDp2Px(x, y)
                return x, y
        errorMessage = ErrorMsgManager().errorCodeToString(ERROR_CODE_GETCOORDINATE)
        raise RuntimeError(errorMessage)

    def getIFrameHtml(self, nodeId=None):
        '''
        :param nodeId:
        :return: 获得指定nodeId的Html
        '''

        self.logger.info('')

        self.switchToNextPage()

        self.getDocument()

        self.wait(WAIT_REFLESH_05_SECOND)
        sendStr = self._pageOperator.requestChildNodes()
        self._networkHandler.send(sendStr)

        if nodeId is None:
            nodeId = self.getIFrameNodeId()
        sendStr = self._pageOperator.getHtml(nodeId)

        result = self._networkHandler.send(sendStr).getResponse()[0]
        self.html = result.get('result').get('outerHTML')
        return self.html

    def getIFrameElementByXpath(self, xpath, nodeId):
        '''
        :param xpath:element的Xpath
        :param nodeId: element所在页面的nodeId
        :return: lxml的ELement对象
        '''
        self.logger.info('xpath ---> ' + xpath)
        html = etree.HTML(self.getIFrameHtml(nodeId))
        self.logger.info(etree.tostring(html))
        return html.xpath(xpath)[0]

    '''
    性能数据
    '''

    def getMemoryInfo(self):
        '''
        获得H5进程占用内存信息
        :return: H5进程占用内存信息
        '''
        self.logger.info('')
        ADB_SHELL = 'adb shell '
        if self._device:
            ADB_SHELL = ADB_SHELL.replace("adb", "adb -s %s" % self._device)
        GET_MEMORY_INFO = ADB_SHELL + 'dumpsys meminfo com.tencent.mm:tools'
        return commandHelper.runCommand(GET_MEMORY_INFO)

    def getCPUInfo(self):
        '''
        获得H5进程占用CPU信息
        :return: H5进程占用CPU信息
        '''
        self.logger.info('')
        ADB_SHELL = 'adb shell '
        if self._device:
            ADB_SHELL = ADB_SHELL.replace("adb", "adb -s %s" % self._device)
        GET_CPU_INFO = ADB_SHELL + ' top -n 1 | grep com.tencent.mm:tools'
        return commandHelper.runCommand(GET_CPU_INFO)

    def setDebugLogMode(self):
        Log().setDebugLogMode()


if __name__ == "__main__":
    pass
