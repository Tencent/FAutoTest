'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
from setuptools import setup, find_packages

NAME = "fastAutoTest-dev"
VERSION = "2.2.4"
AUTHOR = "jaggergan,fitchzheng"
PACKAGES = find_packages()
CLASSIFIERS = [
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "Operating System :: Unix",
    "Programming Language :: Python :: 2.7",
]

INSTALL_REQUIRES = [
    "websocket-client>=0.44.0",
    "uiautomator>=0.3.2",
    "lxml>=4.0.0",
    "bidict>=0.14.0"

]
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    install_requires=INSTALL_REQUIRES
)
