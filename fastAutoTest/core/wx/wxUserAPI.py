# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''

class ByType(object):
    ID = "id"
    NAME = "name"
    XPATH = "xpath"


class ActionType(object):
    CLICK = "click"
    TEXT = "text"
    SCROLL = "scroll"
    RETURN_LAST_PAGE = "returnPage"
    CLOSE_WINDOW = "closeWindow"
    GET_PICKER_RECT = "getRect"
    GET_ELEMENT_TEXT = "getElementText"
    GET_ELEMENT_SRC = "getElementSrc"
    GET_PAGE_HEIGHT = 'getPageHeight'
    GET_ELEMENT_RECT = 'getElementRect'
    GET_JS_VALUE = 'getJsValue'
    IS_ELEMENT_EXIST = 'isElementExist'
    GET_WINDOW_HEIGHT = 'getWindowHeight'
    GET_WINDOW_WIDTH = 'getWindowWidth'
    GET_HTML = "getHTML"
    GET_DOCUMENT = "getDocument"
