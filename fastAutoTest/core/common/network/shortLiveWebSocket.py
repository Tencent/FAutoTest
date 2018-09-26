# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
import json
import threading
import time

from websocket import WebSocketConnectionClosedException

from fastAutoTest.core.common.errormsgmanager import ErrorMsgManager, ERROR_CODE_CONNECT_CLOSED, \
    ERROR_CODE_BAD_REQUEST
from fastAutoTest.core.common.network.websocketdatatransfer import DataTransferCallback
from fastAutoTest.utils.atomicinteger import AtomicInteger
from fastAutoTest.utils.constant import WAIT_REFLESH_60_SECOND, WAIT_REFLESH_40_SECOND, WAIT_REFLESH_2_SECOND, \
    SEND_DATA_ATTEMPT_TOTAL_NUM, WAIT_REFLESH_1_SECOND, WXDRIVER, QQDRIVER
from fastAutoTest.utils.logger import Log

__all__ = [
    'ShortLiveWebSocket'
]


class _NetWorkRequset(object):
    def __init__(self, id, requestData):
        self._id = id
        self._requestData = requestData
        self._response = []
        self._exception = None

    def toSendJsonString(self):
        lastBraceIndex = self._requestData.rfind('}')
        sendJson = self._requestData[:lastBraceIndex] \
                   + ", \"id\"" + ":" + str(self._id) \
                   + self._requestData[lastBraceIndex:]
        return sendJson

    def getResponse(self):
        return self._response

    def addResponse(self, responseStr):
        response = json.loads(responseStr)
        self._checkSuccessOrThrow(response)
        self._response.append(response)

    def getRequestData(self):
        return self._requestData

    def _checkSuccessOrThrow(self, response):
        responseId = response.get('id')
        if responseId is not None:
            if self._id != int(responseId):
                raise RuntimeError("error id")
            del response['id']

    def getException(self):
        return self._exception

    def setException(self, exception):
        self._exception = exception


class ShortLiveWebSocket(DataTransferCallback):
    def __init__(self, webSocketDataTransfer, executor, driver):
        super(ShortLiveWebSocket, self).__init__()
        self._webSocketDataTransfer = webSocketDataTransfer
        self._executor = executor
        self._webSocketDataTransfer.registerCallback(self)

        self._readWriteSyncEvent = threading.Event()
        self._connectSyncEvent = threading.Event()
        self._id = AtomicInteger()
        self._currentRequest = None

        self._quit = False

        self._retryEvent = threading.Event()
        self.driver = driver
        self.logger = Log().getLogger()

    def setUrl(self, url):
        self._webSocketDataTransfer.setUrl(url)

    def isConnected(self):
        return self._webSocketDataTransfer.isConnected()

    def connect(self):
        self._webSocketDataTransfer.connect()
        self._connectSyncEvent.set()

    def disconnect(self):
        self._webSocketDataTransfer.disconnect()
        self._connectSyncEvent.clear()

    def receive(self):
        while not self.isQuit():
            try:
                self._waitForConnectOrThrow()
                self._webSocketDataTransfer.receive()

            except WebSocketConnectionClosedException:
                if self.isQuit():
                    print 'already quit'
                else:
                    pass
            except Exception:
                pass

    def send(self, data, timeout=int(1 * 60)):
        self._waitForConnectOrThrow()
        # 微信小程序和QQ公粽号都需要切换页面
        if self.driver.getDriverType() == WXDRIVER or self.driver.getDriverType == QQDRIVER:
            # 只有点击事件才会导致页面的切换
            if 'x=Math.round((left+right)/2)' in data:
                time.sleep(WAIT_REFLESH_1_SECOND)
            if self.driver.needSwitchNextPage():
                self.driver.switchToNextPage()

        self._currentRequest = _NetWorkRequset(self._id.getAndIncrement(), data)
        currentRequestToJsonStr = self._currentRequest.toSendJsonString()
        self.logger.debug(' ---> ' + currentRequestToJsonStr)

        # scroll操作需要滑动到位置才会有返回，如果是scroll操作则等待，防止超时退出
        if 'synthesizeScrollGesture' in data:
            self._webSocketDataTransfer.send(currentRequestToJsonStr)
            self._retryEvent.wait(WAIT_REFLESH_40_SECOND)
        else:
            for num in range(0, SEND_DATA_ATTEMPT_TOTAL_NUM):
                self.logger.debug(" ---> attempt num: " + str(num))

                if num != 3 and num != 5:
                    self._webSocketDataTransfer.send(currentRequestToJsonStr)
                    self._retryEvent.wait(3)
                else:
                    self.driver.switchToNextPage()
                    time.sleep(WAIT_REFLESH_2_SECOND)
                    self.logger.debug('switch when request:  ' + currentRequestToJsonStr)
                    self._webSocketDataTransfer.send(currentRequestToJsonStr)
                    self._retryEvent.wait(WAIT_REFLESH_2_SECOND)

                if self._readWriteSyncEvent.isSet():
                    break

        self._readWriteSyncEvent.wait(timeout=timeout)
        self._readWriteSyncEvent.clear()
        self._retryEvent.clear()

        self._checkReturnOrThrow(self._currentRequest)

        return self._currentRequest

    def quit(self):
        self._quit = True
        self.disconnect()

    def isQuit(self):
        return self._quit

    def _checkReturnOrThrow(self, netWorkRequest):
        needThrown = (netWorkRequest.getResponse() is None and
                      netWorkRequest.getException() is None)
        if needThrown:
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_BAD_REQUEST)
            raise RuntimeError("%s, request data {%s}" % (errorMsg, netWorkRequest.getRequestData()))

    def _waitForConnectOrThrow(self):
        if self._webSocketDataTransfer.isConnected():
            return

        self._connectSyncEvent.wait(WAIT_REFLESH_60_SECOND)

        if not self._webSocketDataTransfer.isConnected():
            errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_CONNECT_CLOSED)
            raise RuntimeError("connect %s timeout, %s" % (self._webSocketDataTransfer.getUrl(), errorMsg))

    def onMessage(self, message):
        if self._currentRequest is None:
            raise RuntimeError("current request is None")
        if message is not None:
            self._currentRequest.addResponse(message)
            # 只有当response带有id，所有response才接收完
            if json.loads(message).get('id') is not None:
                self._retryEvent.set()
                self._readWriteSyncEvent.set()
            self.logger.debug(' ---> ' + message)
        else:
            self.logger.debug(' --->' + 'message is None')
