import logging
import sys
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''

class Log(object):
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, name='default'):
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.INFO)
        if not self.logger.handlers:
            format = logging.Formatter("%(asctime)-8s %(thread)d %(funcName)s %(message)s")
            consoleHandler = logging.StreamHandler(sys.stdout)
            consoleHandler.setFormatter(format)
            self.logger.addHandler(consoleHandler)

    def setLevel(self, level):
        self.logger.setLevel(level)

    def getLogger(self):
        return self.logger

    def setDebugLogMode(self):
        self.logger.setLevel(self.DEBUG)
