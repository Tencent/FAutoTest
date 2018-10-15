# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''

import json
import urllib2

import bidict
from websocket import create_connection

from fastAutoTest.core.common.errormsgmanager import *
from fastAutoTest.utils.adbHelper import AdbHelper
from fastAutoTest.utils.commandHelper import runCommand
from fastAutoTest.utils.common import OS
from fastAutoTest.utils.logger import Log

_ADB_GET_TOP_ACTIVITY_CMD = {
    "Darwin": "adb shell dumpsys activity top | grep ACTIVITY",  # Mac os 下查找字符串是grep
    "Linux": "adb shell dumpsys activity top | grep ACTIVITY",  # Mac os 下查找字符串是grep
    "Windows": "adb shell dumpsys activity top | findstr ACTIVITY"  # windows 下查找字符串是findstr
}

_ADB_GET_WEBVIEW_TOOLS_CMD = {
    "Darwin": "adb shell cat /proc/net/unix | grep webview_devtools_remote_%s",  # Mac os 下查找字符串是grep
    "Linux": "adb shell cat /proc/net/unix | grep webview_devtools_remote_%s",  # Mac os 下查找字符串是grep
    "Windows": "adb shell cat /proc/net/unix | findstr webview_devtools_remote_%s"  # windows 下查找字符串是findstr
}

MODE_NORMAL = 0
MODE_EMBEDDED_H5 = 1


class WxWebSocketDebugUrlFetcher(object):
    DEFAULT_LOCAL_FORWARD_PORT = 9223
    # 根据dict中存储的数量来获得新添加页面的名称
    pageMap = {1: 'event',
               2: 'first',
               3: 'second',
               4: 'third',
               5: 'fourth',
               6: 'fifth'}

    def __init__(self, device, localForwardPort=None):
        self._device = device
        self._localForwardPort = localForwardPort if localForwardPort is not None \
            else WxWebSocketDebugUrlFetcher.DEFAULT_LOCAL_FORWARD_PORT
        self._webSocketDebugUrl = None
        # 通过dic来管理页面
        self.pageUrlDict = bidict.bidict()
        self.logger = Log().getLogger()
        self.mode = MODE_NORMAL

    def fetchWebSocketDebugUrl(self, refetch=False):
        # 如果没有获取或者需要重新获取debug url，那么获取一次，否则直接返回
        if self._webSocketDebugUrl is None:
            self._fetchInner()
        if refetch:
            self._webSocketDebugUrl = self._fetchWebSocketDebugUrl(self._localForwardPort)
        return self._webSocketDebugUrl

    def getDevice(self):
        return self._device

    def getForwardPort(self):
        return self._localForwardPort

    def _fetchInner(self):
        # 先获取微信appbrand进程Pid
        pid = WxWebSocketDebugUrlFetcher._fetchWeixinToolsProcessPid(device=self._device)

        # 重定向端口
        WxWebSocketDebugUrlFetcher._forwardLocalPort(self._localForwardPort, pid, device=self._device)

        # 获取本地http://localhost:{重定向端口}/json返回的json数据，提取里面的webSocketDebuggerUrl字段值
        self._webSocketDebugUrl = self._fetchWebSocketDebugUrl(self._localForwardPort)

    @staticmethod
    def _fetchWeixinToolsProcessPid(device=None):
        osName = OS.getPlatform()
        cmd = _ADB_GET_TOP_ACTIVITY_CMD[osName]
        stdout, stdError = runCommand(AdbHelper.specifyDeviceOnCmd(cmd, device))
        strlist = stdout.split('pid=')
        pid = strlist[1].split("\r\n")[0]
        webviewCmd = _ADB_GET_WEBVIEW_TOOLS_CMD[osName] % (pid)

        # 验证是否启动了小程序webview
        try:
            webStdout, webStdError = runCommand(AdbHelper.specifyDeviceOnCmd(webviewCmd, device))
        except:
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_NOT_ENTER_XCX)
            raise RuntimeError(errorMsg)
        return pid

    @staticmethod
    def _forwardLocalPort(localPort, pid, device=None):
        cmd = "adb forward tcp:%s localabstract:webview_devtools_remote_%s" % (localPort, pid)
        runCommand(AdbHelper.specifyDeviceOnCmd(cmd, device))

    def _fetchWebSocketDebugUrl(self, localPort):
        import time
        localUrl = "http://localhost:%s/json" % localPort
        errorMsg = None
        resultUrl = None

        # 去掉代理
        urllib2.getproxies = lambda: {}

        try:
            nums = 0
            while None == resultUrl and nums < 8:
                response = urllib2.urlopen(localUrl)
                responseJson = json.loads(response.read())
                if len(responseJson) != 1:

                    self._cleanJsonData(responseJson)

                    resultUrl = self._handleAndReturnWebSocketDebugUrl(responseJson)
                    self.logger.debug('websocket --> ' + resultUrl)
                    return resultUrl
                else:
                    nums = nums + 1
                    self.logger.debug('retry fetch num ---> ' + str(nums))
                    time.sleep(1)

        except IndexError:
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_NOT_ENABLE_DEBUG_MODE)
        except LookupError:
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_NOT_ENTER_XCX)
        except AttributeError:
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_NOT_GET_XCX_PAGE_INFO)
        except Exception:
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_CONFIG_PROXY)
        raise RuntimeError(errorMsg)

    # 去掉file://开头的脏数据
    def _cleanJsonData(self, responseJson):
        removeList = []
        for response in responseJson:
            if u'file:///' in response['url']:
                removeList.append(response)
        for i in removeList:
            responseJson.remove(i)

    def _handleAndReturnWebSocketDebugUrl(self, responseJson):
        responseLength = len(responseJson)
        pageUrlDictLength = len(self.pageUrlDict)
        # 如果第一次进入小程序，当前加载的dict为空
        if pageUrlDictLength == 0:
            # 考虑正常的小程序，有两个链接，一个是空的server,一个是首页面。
            if responseLength == 2:
                self.mode = MODE_NORMAL
                return self._initWebSocketUrlWithTwoPage(responseJson)
            # 如果是小程序内嵌H5的情况，有三个链接，其中两个ServiceWeChat的URL，一个H5的URL。
            if responseLength == 3:
                self.mode = MODE_EMBEDDED_H5
                return self._initWebSocketUrlWithThreePage(responseJson)

        # 如果返回的大于当前打开的，说明要开启新的页面
        # 有两种情况，一种是打开正常的小程序页面，启动一个新链接，另一种是打开嵌套H5的小程序页面，会启动两个链接
        elif responseLength > pageUrlDictLength:
            if responseLength - pageUrlDictLength == 1:
                for i in range(responseLength):
                    message = self._getPageFeature(responseJson[i]["webSocketDebuggerUrl"])
                    if self.pageUrlDict.inv.get(message) is None:
                        self.pageUrlDict.update({self.pageMap.get(pageUrlDictLength + 1): message})
                        return responseJson[i]["webSocketDebuggerUrl"]
            elif responseLength - pageUrlDictLength == 2:
                h5Url = ''
                for i in range(responseLength):
                    message = self._getPageFeature(responseJson[i]["webSocketDebuggerUrl"])
                    if self.pageUrlDict.inv.get(message) is None:
                        self.pageUrlDict.update({self.pageMap.get(pageUrlDictLength + 1): message})
                        if 'https://servicewechat.com/' not in responseJson[i]["url"]:
                            h5Url = responseJson[i]["webSocketDebuggerUrl"]
                return h5Url
            else:
                raise AttributeError()

        # 如果返回的小于当前打开的，说明要删除一个页面
        # 有两种情况，一种是关闭正常的小程序页面，删除一个链接，另一种是关闭嵌套H5的小程序页面，需要删除两个链接
        elif responseLength < pageUrlDictLength:
            if pageUrlDictLength - responseLength == 1:
                sencondLastPageMessage = self.pageUrlDict.get(self.pageMap.get(pageUrlDictLength - 1))
                shouldReturnUrl = None
                del self.pageUrlDict[self.pageMap.get(pageUrlDictLength)]
                for i in range(responseLength):
                    message = self._getPageFeature(responseJson[i]["webSocketDebuggerUrl"])
                    if message == sencondLastPageMessage:
                        shouldReturnUrl = responseJson[i]["webSocketDebuggerUrl"]
                return shouldReturnUrl
            elif pageUrlDictLength - responseLength == 2:
                sencondLastPageMessage = self.pageUrlDict.get(self.pageMap.get(pageUrlDictLength - 2))
                shouldReturnUrl = None
                del self.pageUrlDict[self.pageMap.get(pageUrlDictLength)]
                del self.pageUrlDict[self.pageMap.get(pageUrlDictLength - 1)]
                for i in range(responseLength):
                    message = self._getPageFeature(responseJson[i]["webSocketDebuggerUrl"])
                    if message == sencondLastPageMessage:
                        shouldReturnUrl = responseJson[i]["webSocketDebuggerUrl"]
                return shouldReturnUrl


        # 如果返回的等于当前打开的，有两种情况。一种是两个URL时，返回最后一个webSocketUrl。一种是当有三个URL，小程序内嵌H5 URL时，返回内嵌的H5 URL。
        elif responseLength == pageUrlDictLength:
            if self.mode == MODE_NORMAL:
                lastPageMessage = self.pageUrlDict.get(self.pageMap.get(pageUrlDictLength))
                for i in range(responseLength):
                    message = self._getPageFeature(responseJson[i]["webSocketDebuggerUrl"])
                    if message == lastPageMessage:
                        return responseJson[i]["webSocketDebuggerUrl"]
                #     如果都为空，则在当前页面进行了跳转，因此要更新dict中的特征
                # 依次连接返回的所有page的websocketurl，找到一个更新后的页面
                for response in responseJson:
                    websocketUrl = response["webSocketDebuggerUrl"]
                    pageFeature = self._getPageFeature(websocketUrl)

                    if self.pageUrlDict.inv.get(pageFeature) is None:
                        self.pageUrlDict.update({self.pageMap.get(pageUrlDictLength): pageFeature})
                        return websocketUrl
            else:
                return self.pageUrlDict.get(1)

    def _initWebSocketUrlWithTwoPage(self, responseJson):
        eventData = u'[object Text][object HTMLDivElement][object Text]'
        responseLength = 2
        pageUrlDictLength = len(self.pageUrlDict)
        for i in range(responseLength):
            message = self._getPageFeature(responseJson[i]["webSocketDebuggerUrl"])
            if message == eventData:
                self.pageUrlDict.update({self.pageMap.get(pageUrlDictLength + 1): message})
                if i == 0:
                    firstMessage = self._getPageFeature(responseJson[1]["webSocketDebuggerUrl"])
                    self.pageUrlDict.update({self.pageMap.get(pageUrlDictLength + 2): firstMessage})
                    return responseJson[1]["webSocketDebuggerUrl"]
                else:
                    firstMessage = self._getPageFeature(responseJson[0]["webSocketDebuggerUrl"])
                    self.pageUrlDict.update({self.pageMap.get(pageUrlDictLength + 2): firstMessage})
                    return responseJson[0]["webSocketDebuggerUrl"]

    def _initWebSocketUrlWithThreePage(self, responseJson):
        responseWesocketUrlDict = {}
        responseUrlList = []
        serviceUrlList = []
        h5Url = []
        responseLength = 3

        for i in range(responseLength):
            response = responseJson[i]
            url = response['url']
            webSocketUrl = response['webSocketDebuggerUrl']
            responseUrlList.append(url)
            responseWesocketUrlDict[url] = webSocketUrl
        for url in responseUrlList:
            if u"servicewechat" in url:
                serviceUrlList.append(url)
            else:
                h5Url.append(url)
        if len(serviceUrlList) != 2 or len(h5Url) != 1:
            raise AttributeError()
        else:
            url = ''
            for url in serviceUrlList:
                webSocketUrl = responseWesocketUrlDict.get(url)
                print webSocketUrl
                webSocketConn = create_connection(url=webSocketUrl)
                webSocketConn.send(
                    '{"id": 1,"method": "Runtime.evaluate","params": {"expression": "srcs = document.body.childNodes[0].getAttribute(\'src\')"}}'
                )
                results = webSocketConn.recv()
                result = json.loads(results)
                webSocketConn.close()
                if result.get('result').get('result').get('type') == u'string':
                    url = result.get('result').get('result').get('value')
                    break
            if url not in h5Url[0]:
                raise AttributeError()
            else:
                self.pageUrlDict.forceupdate({1: responseWesocketUrlDict.get(h5Url[0])})
                self.pageUrlDict.forceupdate({2: responseWesocketUrlDict.get(serviceUrlList[0])})
                self.pageUrlDict.forceupdate({3: responseWesocketUrlDict.get(serviceUrlList[1])})
                return responseWesocketUrlDict.get(h5Url[0])

    def _getPageFeature(self, url):
        import time
        retry = True
        nums = 0
        message = ''
        while (retry and nums < 8):
            try:
                webSocketConn = create_connection(url=url)

                webSocketConn.send(
                    '{"id": 1,"method": "Runtime.evaluate","params": {"expression": "var allNodeList = [];function getChildNode(node){var nodeList = node.childNodes;for(var i = 0;i < nodeList.length;i++){var childNode = nodeList[i];allNodeList.push(childNode);getChildNode(childNode);}};getChildNode(document.body);"}}'
                )
                webSocketConn.recv()
                webSocketConn.send(
                    '{"id": 2,"method": "Runtime.evaluate","params": {"expression": "allNodeEle=\'\'"}}'
                )
                webSocketConn.recv()
                webSocketConn.send(
                    '{"id": 3,"method": "Runtime.evaluate","params": {"expression": "for(j = 0; j < allNodeList.length; j++) {allNodeEle = allNodeEle+allNodeList[j];}"}}'
                )

                results = webSocketConn.recv()

                self.logger.debug(results)

                result = json.loads(results)
                retry = True if result.get('result').get('wasThrown') is True or \
                                result.get('result').get('result').get('value') == u'' or \
                                result.get('result').get('result').get('type') == u'undefined' else False
                if retry:
                    time.sleep(2)
                    nums = nums + 1
                    webSocketConn.close()
                    Log().getLogger().info('retry getFeatur ---> ' + str(nums))
                    continue
                else:
                    message = result['result']['result']['value']
                    retry = False
                webSocketConn.close()
                return message
            except:
                continue
        if retry or message == '':
            raise AttributeError()

    def needSwitchNextPage(self):
        import json
        import urllib2
        localUrl = "http://localhost:9223/json"

        # 去掉代理
        urllib2.getproxies = lambda: {}

        response = urllib2.urlopen(localUrl)
        responseJson = json.loads(response.read())
        return len(responseJson) != len(self.pageUrlDict)


if __name__ == "__main__":
    pass
