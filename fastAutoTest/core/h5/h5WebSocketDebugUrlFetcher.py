# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''

from fastAutoTest.core.common.errormsgmanager import *
from fastAutoTest.utils.adbHelper import AdbHelper
from fastAutoTest.utils.commandHelper import runCommand
from fastAutoTest.utils.common import OS
from fastAutoTest.utils.logger import Log
import time

_ADB_FIND_STR_CMD = {
    "Darwin": "adb shell ps | grep -w com.tencent.mm:tools",  # Mac os 下查找字符串是grep
    "Linux": "adb shell ps | grep -w com.tencent.mm:tools",  # Mac os 下查找字符串是grep
    "Windows": "adb shell ps | findstr /e com.tencent.mm:tools"  # windows 下查找字符串是findstr
}


class H5WebSocketDebugUrlFetcher(object):
    DEFAULT_LOCAL_FORWARD_PORT = 9222

    def __init__(self, device, localForwardPort=None):
        self._device = device
        self._localForwardPort = localForwardPort if localForwardPort is not None \
            else H5WebSocketDebugUrlFetcher.DEFAULT_LOCAL_FORWARD_PORT
        self._webSocketDebugUrl = None

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
        # 先获取微信Tools进程Pid
        pid = H5WebSocketDebugUrlFetcher._fetchWeixinToolsProcessPid(device=self._device)

        # 重定向端口
        H5WebSocketDebugUrlFetcher._forwardLocalPort(self._localForwardPort, pid, device=self._device)

        # 获取本地http://localhost:{重定向端口}/json返回的json数据，提取里面的webSocketDebuggerUrl字段值
        self._webSocketDebugUrl = self._fetchWebSocketDebugUrl(self._localForwardPort)

    @staticmethod
    def _fetchWeixinToolsProcessPid(device=None):

        """

        PS命名结果字段格式为8元祖，格式为：USER     PID   PPID  VSIZE  RSS  WCHAN  PC  NAME

        各字段解释
        USER：  进程的当前用户；
        PID   ： 毫无疑问, process ID的缩写，也就进程号；
        PPID  ：process parent ID，父进程ID
        VSIZE  ： virtual size，进程虚拟地址空间大小；
        RSS    ： 进程正在使用的物理内存的大小；
        WCHAN  ：进程如果处于休眠状态的话，在内核中的地址；
        PC  ： program counter，
        NAME: process name，进程的名称

        """
        osName = OS.getPlatform()
        cmd = _ADB_FIND_STR_CMD[osName]

        stdout = H5WebSocketDebugUrlFetcher._getProcessInfo(cmd, device)

        weixinProcessInfoLine = None
        for processInfo in stdout.split("\r\r\n"):
            if "com.tencent.mm:tools" in processInfo:
                weixinProcessInfoLine = processInfo
                break

        if weixinProcessInfoLine is None:
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_NOT_FOUND_WEIXIN_TOOLS_PROCESS)
            raise RuntimeError(errorMsg)

        weixinProcessInfo = weixinProcessInfoLine.split()
        return H5WebSocketDebugUrlFetcher._handlePhoneCompat(weixinProcessInfo)

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
    def _handlePhoneCompat(weixinProcessInfo):

        # 这里建立ps命令返回结果行字段数和pid字段index的映射
        pidIndexMap = {9: 1,  # 三星的手机是9元祖，第二列为pid index
                       5: 0,  # 华为的手机是5元祖，第一列为pid index
                       10: 5,  # 当微信出现异常时可能出现两个tools，那么选择第二个。
                       18: 10
                       }

        fieldCount = len(weixinProcessInfo)
        pidIndex = pidIndexMap.get(fieldCount, -1)

        if pidIndex >= 0:
            return int(weixinProcessInfo[pidIndex])
        else:
            raise RuntimeError(ErrorMsgManager().errorCodeToString(ERROR_CODE_NOT_ENABLE_DEBUG_MODE))

    @staticmethod
    def _forwardLocalPort(localPort, pid, device=None):
        cmd = "adb forward tcp:%s localabstract:webview_devtools_remote_%s" % (localPort, pid)
        runCommand(AdbHelper.specifyDeviceOnCmd(cmd, device))

    def _fetchWebSocketDebugUrl(self, localPort):
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
                    for responseItem in responseJson:
                        descriptionDict = json.loads(responseItem['description'])
                        if descriptionDict['empty'] == False:
                            resultUrl = responseItem["webSocketDebuggerUrl"]
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



if __name__ == "__main__":
    pass
