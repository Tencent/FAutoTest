# coding=utf-8
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
from fastAutoTest.core.wx.wxEngine import WxDriver
import os

# 进入企鹅医典小程序
if __name__ == '__main__':
    wxDriver = WxDriver()
    wxDriver.initDriver()
    # 点击全部疾病
    wxDriver.clickElementByXpath('/html/body/div/div[1]/div[2]/div[1]/a')
    wxDriver.clickFirstElementByText('肺癌')
    wxDriver.returnLastPage()
    wxDriver.returnLastPage()
    # 截图
    dirPath = os.path.split(os.path.realpath(__file__))[0]
    PIC_SRC = os.path.join(dirPath, 'pic.png')
    wxDriver.d.screenshot(PIC_SRC)
    wxDriver.close()
