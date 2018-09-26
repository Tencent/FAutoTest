# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''

"""
设备连接类错误信息
"""
ERROR_CODE_DEVICE_NOT_CONNECT = 1000  # 设备没有连上
ERROR_CODE_MULTIPLE_DEVICE = 1001  # 有多个设备连接，但是使用时并没有指定具体设备
ERROR_CODE_NOT_CONFIG_ENV = 1002  # 没有配置环境变量

"""
获取debug url相关错误
"""
ERROR_CODE_MULTIPLE_URL = 2000  # 多个debug URL
ERROR_CODE_NOT_ENABLE_DEBUG_MODE = 2001  # 没有打开调试模式、
ERROR_CODE_NOT_ENTER_H5 = 2002  # 打开了调试模式, 但是当前并没有进入H5页面
ERROR_CODE_NOT_FOUND_WEIXIN_TOOLS_PROCESS = 2003  # 找不到微信Tools进程
ERROR_CODE_CONFIG_PROXY = 2004  # 无法获取debug url，检查是否配置了代理
ERROR_CODE_NOT_ENTER_XCX = 2005  # 未在小程序首屏进行初始化
ERROR_CODE_NOT_GET_XCX_PAGE_INFO = 2006  # 获取小程序页面特征失败
ERROR_CODE_GET_PID_WRONG = 2007  # 检测到小程序进程，获取PID失败

"""
协议相关操作错误
"""
ERROR_CODE_BAD_REQUEST = 3000
ERROR_CODE_REQUEST_EXCEPTION = 3001
ERROR_CODE_REQUEST_NOT_MATCH_RESPONSE = 3002

"""
websocket链接相关错误
"""
ERROR_CODE_CONNECT_CLOSED = 4000

"""
运行时错误
"""
ERROR_CODE_GETCOORDINATE = 5000  # 获取Element坐标失败，该Element不存在
ERROR_CODE_SETUP_FRAME_PAGE = 5001  # Body标签中的IFrame页面不存在或还未加载

"""
未知错误
"""
ERROR_CODE_UNKNOWN = -999999  # 未知错误

_ERROR_CODE_SET = [
    ERROR_CODE_NOT_CONFIG_ENV,
    ERROR_CODE_DEVICE_NOT_CONNECT,
    ERROR_CODE_MULTIPLE_DEVICE,
    ERROR_CODE_MULTIPLE_URL,
    ERROR_CODE_NOT_ENABLE_DEBUG_MODE,
    ERROR_CODE_NOT_ENTER_H5,
    ERROR_CODE_NOT_FOUND_WEIXIN_TOOLS_PROCESS,
    ERROR_CODE_CONFIG_PROXY,
    ERROR_CODE_BAD_REQUEST,
    ERROR_CODE_REQUEST_EXCEPTION,
    ERROR_CODE_REQUEST_NOT_MATCH_RESPONSE,
    ERROR_CODE_CONNECT_CLOSED,
    ERROR_CODE_UNKNOWN,
    ERROR_CODE_NOT_ENTER_XCX,
    ERROR_CODE_NOT_GET_XCX_PAGE_INFO,
    ERROR_CODE_GET_PID_WRONG,
    ERROR_CODE_GETCOORDINATE,
    ERROR_CODE_SETUP_FRAME_PAGE
]

_ERROR_MSG_MAPPING = {
    ERROR_CODE_NOT_CONFIG_ENV: "执行adb命令失败，请检查是否配置系统环境变量",
    ERROR_CODE_DEVICE_NOT_CONNECT: "没有设备连上，请用adb device确认是否有设备连接到PC",
    ERROR_CODE_MULTIPLE_DEVICE: "当前有多个设备连接到PC，请创建H5Driver时指定要操作的设备",
    ERROR_CODE_MULTIPLE_URL: "检测到多个debug url",
    ERROR_CODE_NOT_ENABLE_DEBUG_MODE: "请在微信端打开H5调试模式,或者后台杀死微信进程后重试",
    ERROR_CODE_NOT_ENTER_H5: "在执行脚本前，先进入H5页面",
    ERROR_CODE_NOT_FOUND_WEIXIN_TOOLS_PROCESS: "找不到微信Tools进程",
    ERROR_CODE_CONFIG_PROXY: "无法获取debug url，并检查是否配置了代理，是否已经建立了websocket连接未关闭",
    ERROR_CODE_NOT_ENTER_XCX: "获取小程序pid失败，请检查是否在小程序首屏进行初始化",
    ERROR_CODE_NOT_GET_XCX_PAGE_INFO: "获取小程序页面特征失败",
    ERROR_CODE_BAD_REQUEST: "操作错误，请检查",
    ERROR_CODE_REQUEST_EXCEPTION: "操作发生异常",
    ERROR_CODE_REQUEST_NOT_MATCH_RESPONSE: "请求和响应不匹配",
    ERROR_CODE_CONNECT_CLOSED: "websocket链接已关闭",
    ERROR_CODE_GET_PID_WRONG: "检测到小程序进程，获取PID失败",
    ERROR_CODE_UNKNOWN: "未知错误",
    ERROR_CODE_GETCOORDINATE: "获取Element坐标失败，该Element不存在",
    ERROR_CODE_SETUP_FRAME_PAGE: "Body标签中的IFrame页面不存在或还未加载"

}


class ErrorMsgManager(object):
    _instance = None

    """
    单例模式
    """

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ErrorMsgManager, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def errorCodeToString(self, errorCode):
        if errorCode not in _ERROR_CODE_SET:
            errorCode = ERROR_CODE_UNKNOWN

        return _ERROR_MSG_MAPPING[errorCode]


if __name__ == "__main__":
    errorMgr = ErrorMsgManager()
    print(errorMgr.errorCodeToString(0))
