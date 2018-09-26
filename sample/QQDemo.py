# coding=utf-8
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
from fastAutoTest.core.qq.qqEngine import QQDriver

# 从动态 -> 动漫进入
if __name__ == '__main__':
    qqDriver = QQDriver()
    qqDriver.initDriver()
    qqDriver.clickFirstElementByText('英雄救美，这也太浪漫了')
    qqDriver.returnLastPage()
    qqDriver.clickElementByXpath('//*[@id="app"]/div/ul/li[2]')
    qqDriver.returnLastPage()
    qqDriver.close()
