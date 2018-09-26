# coding=utf-8
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
from fastAutoTest.core.h5.h5Engine import H5Driver

# http://h5.baike.qq.com/mobile/enter.html 从微信进入此链接，首屏加载完后执行脚本
if __name__ == '__main__':
    h5Driver = H5Driver()
    h5Driver.initDriver()
    h5Driver.clickElementByXpath('/html/body/div[1]/div/div[3]/p')
    h5Driver.clickFirstElementByText('白内障')
    h5Driver.returnLastPage()
    h5Driver.returnLastPage()
    print(h5Driver.getElementTextByXpath('/html/body/div[1]/div/div[3]/p'))
    h5Driver.close()

