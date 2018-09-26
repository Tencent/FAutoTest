# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''

import time

import bidict

from fastAutoTest.core.common.errormsgmanager import *
from fastAutoTest.utils.adbHelper import AdbHelper
from fastAutoTest.utils.commandHelper import runCommand
from fastAutoTest.utils.common import OS
from fastAutoTest.utils.logger import Log

# 找到QQ的Tools的PID
_ADB_FIND_QQ_STR_CMD = {
    "Darwin": "adb shell ps | grep com.tencent.mobileqq:tool",  # Mac os 下查找字符串是grep
    "Linux": "adb shell ps | grep com.tencent.mobileqq:tool",  # Mac os 下查找字符串是grep
    "Windows": "adb shell ps | findstr com.tencent.mobileqq:tool"  # windows 下查找字符串是findstr
}


_ADB_PACKAGE_QQ = "com.tencent.mobileqq"
TYPE_QQ = "qq"


class QQWebSocketDebugUrlFetcher(object):
    DEFAULT_LOCAL_FORWARD_PORT = 9222

    def __init__(self, device, localForwardPort=None):
        self._device = device
        self._localForwardPort = localForwardPort if localForwardPort is not None \
            else QQWebSocketDebugUrlFetcher.DEFAULT_LOCAL_FORWARD_PORT
        self._webSocketDebugUrl = None
        self.type = ''

        self.pageUrlDict = bidict.bidict()
        self.logger = Log().getLogger()

    def fetchWebSocketDebugUrl(self, refetch=False):
        # 如果没有获取或者需要重新获取debug url，那么获取一次，否则直接返回
        if self._webSocketDebugUrl is None or refetch:
            self._fetchInner()

        return self._webSocketDebugUrl

    def getDevice(self):
        return self._device

    def getForwardPort(self):
        return self._localForwardPort

    def _fetchInner(self):

        self.logger.debug('')

        pid = QQWebSocketDebugUrlFetcher._fetchQQToolsProcessPid(device=self._device)
        QQWebSocketDebugUrlFetcher._forwardLocalPort(self._localForwardPort, pid, device=self._device)

        # 获取本地http://localhost:{重定向端口}/json返回的json数据，提取里面的webSocketDebuggerUrl字段值
        self._webSocketDebugUrl = self._fetchWebSocketDebugUrl(self._localForwardPort)

    @staticmethod
    def _fetchQQToolsProcessPid(device=None):

        osName = OS.getPlatform()
        cmd = _ADB_FIND_QQ_STR_CMD[osName]

        stdout = QQWebSocketDebugUrlFetcher._getProcessInfo(cmd, device)

        QQProcessInfoLine = None
        for processInfo in stdout.split("\r\r\n"):
            if "com.tencent.mobileqq:tool" in processInfo:
                QQProcessInfoLine = processInfo
                break

        if QQProcessInfoLine is None:
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_NOT_FOUND_WEIXIN_TOOLS_PROCESS)
            raise RuntimeError(errorMsg)

        QQProcessInfo = QQProcessInfoLine.split()
        return QQWebSocketDebugUrlFetcher._handlePhoneCompat(QQProcessInfo)

    @staticmethod
    def _getProcessInfo(cmd, device):
        nums = 0
        retry = True
        stdout = ''
        while (retry and nums < 8):
            try:
                stdout, stdError = runCommand(AdbHelper.specifyDeviceOnCmd(cmd, device))
                retry = False
            except:
                nums = nums + 1
                time.sleep(1)
                Log().getLogger().debug('open port mapping ---> retry ' + str(nums))
        return stdout

    @staticmethod
    def _handlePhoneCompat(processInfo):

        # 这里建立ps命令返回结果行字段数和pid字段index的映射
        pidIndexMap = {9: 1,  # 三星的手机是9元祖，第二列为pid index
                       5: 0,  # 华为的手机是5元祖，第一列为pid index
                       10: 5,  # 当微信出现异常时可能出现两个tools，那么选择第二个。
                       18: 10
                       }

        fieldCount = len(processInfo)
        pidIndex = pidIndexMap.get(fieldCount, -1)

        if pidIndex >= 0:
            return int(processInfo[pidIndex])
        else:
            raise RuntimeError(ErrorMsgManager().errorCodeToString(ERROR_CODE_NOT_ENABLE_DEBUG_MODE))

    @staticmethod
    def _forwardLocalPort(localPort, pid, device=None):
        cmd = "adb forward tcp:%s localabstract:webview_devtools_remote_%s" % (localPort, pid)
        runCommand(AdbHelper.specifyDeviceOnCmd(cmd, device))

    def _fetchWebSocketDebugUrl(self, localPort):
        self.logger.debug('')
        import json
        import urllib2
        errorMsg = None
        resultUrl = None

        localUrl = "http://localhost:%s/json" % localPort

        # 去掉代理
        urllib2.getproxies = lambda: {}

        try:
            nums = 0
            while None == resultUrl and nums < 8:
                response = urllib2.urlopen(localUrl)
                responseJson = json.loads(response.read())
                if len(responseJson) != 0:
                    resultUrl = self._handleAndReturnWebSocketDebugUrl(responseJson)
                    self.logger.debug('websocket --> ' + resultUrl)
                    return resultUrl
                else:
                    nums = nums + 1
                    Log().getLogger().debug('retry fetch num ---> ' + str(nums))
                    time.sleep(1)

        except Exception:
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_CONFIG_PROXY)
        if not errorMsg:
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_NOT_ENTER_H5)
        raise RuntimeError(errorMsg)

    # 按顺序记录打开页面，key为打开页面的顺序，value为打开页面的websocketUrl。
    def _handleAndReturnWebSocketDebugUrl(self, responseJson):
        import json
        responseLenth = 0
        # 只记录有效页面的数量
        for i in range(len(responseJson)):
            response = responseJson[i]
            if response['type'] == u'page' and json.loads(response['description'])['empty'] == False:
                responseLenth = responseLenth + 1

        pageUrlDictLength = len(self.pageUrlDict)
        if pageUrlDictLength == 0:
            self.logger.debug('pageUrlDictLength == 0:')
            for i in range(responseLenth):
                response = responseJson[i]
                if response['type'] == u'page' and json.loads(response['description'])['empty'] == False:
                    self.pageUrlDict.update({pageUrlDictLength + 1: response['webSocketDebuggerUrl']})
                    return response['webSocketDebuggerUrl']
        elif responseLenth > pageUrlDictLength:
            self.logger.debug('responseLenth > pageUrlDictLength')
            for i in range(responseLenth):
                response = responseJson[i]
                if response['type'] == u'page' and json.loads(response['description'])['empty'] == False:
                    if self.pageUrlDict.inv.get(response['webSocketDebuggerUrl']) is None:
                        self.pageUrlDict.update({pageUrlDictLength + 1: response['webSocketDebuggerUrl']})
                        return response['webSocketDebuggerUrl']
        elif responseLenth < pageUrlDictLength:
            self.logger.debug('responseLenth < pageUrlDictLength')
            sencondLastPageUrl = self.pageUrlDict.get(pageUrlDictLength - 1)
            del self.pageUrlDict[pageUrlDictLength]
            return sencondLastPageUrl
        else:
            self.logger.debug('responseLenth == pageUrlDictLength')
            lastPageUrl = self.pageUrlDict.get(pageUrlDictLength)
            return lastPageUrl

    def needSwitchNextPage(self):
        import json
        import urllib2
        localUrl = "http://localhost:9223/json"

        # 去掉代理
        urllib2.getproxies = lambda: {}

        response = urllib2.urlopen(localUrl)
        responseJson = json.loads(response.read())
        return len(responseJson) != len(self.pageUrlDict)

    def getType(self):
        return self.type


if __name__ == "__main__":
    pass
