# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
import atexit
import sys


class VMShutDownHandler(object):
    """
    虚拟机正常关闭时的回调接口，一般做一些环境清理工作
    """

    def __init__(self):
        self._shutDownCallbacks = []

    def registerToVM(self):
        atexit.register(self._handleVMShutDown)

    def _handleVMShutDown(self):
        for func, args, kwargs in self._shutDownCallbacks:
            func(*args, **kwargs)

    def registerVMShutDownCallback(self, func, *args, **kwargs):
        self._shutDownCallbacks.append((func, args, kwargs))


class UncaughtExceptionHandler(object):
    """
    虚拟机发生异常退出时的回调接口，一般做一些环境清理工作
    """

    _callbacks = []

    @staticmethod
    def init():
        sys.excepthook = UncaughtExceptionHandler._handleUncaughtException

    @staticmethod
    def _handleUncaughtException(exctype, value, tb):
        for func in UncaughtExceptionHandler._callbacks:
            func(exctype, value, tb)
        raise Exception(exctype)

    @staticmethod
    def registerUncaughtExceptionCallback(func):
        UncaughtExceptionHandler._callbacks.append(func)

    @staticmethod
    def removeHook():
        sys.excepthook = None


if __name__ == "__main__":
    pass
