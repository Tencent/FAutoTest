# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
from fastAutoTest.core.wx.wxUserAPI import ActionType
from fastAutoTest.core.wx.wxUserAPI import ByType


class WxCommandManager(object):
    # 使用$$可以作为格式化时的转义
    _elementMap = {
        ByType.ID: "$$('#$id')[0]",
        ByType.NAME: "$$('.$name')[$index]",
        ByType.XPATH: "var xpath ='$xpath';"
                      "xpath_obj = document.evaluate(xpath,document,null, XPathResult.ANY_TYPE, null);"
                      "var button = xpath_obj.iterateNext()"
    }

    # doCommandWithElement中执行的参数
    _jsActionMap = {

        ActionType.GET_ELEMENT_RECT: ";left=Math.round(button.getBoundingClientRect().left);"
                                     "right=Math.round(button.getBoundingClientRect().right);"
                                     "bottom=Math.round(button.getBoundingClientRect().bottom);"
                                     "topp=Math.round(button.getBoundingClientRect().top);"
                                     "x=Math.round((left+right)/2);"
                                     "y=Math.round((topp+bottom)/2);",
        ActionType.IS_ELEMENT_EXIST: ";button",
        ActionType.GET_ELEMENT_TEXT: ";button.textContent;",
        ActionType.GET_ELEMENT_SRC: ";button.getAttribute('src')",
    }

    _methodMap = {
        ActionType.GET_DOCUMENT: "DOM.getDocument",
        ActionType.GET_HTML: "DOM.getOuterHTML",
        ActionType.SCROLL: "Input.synthesizeScrollGesture",
        ActionType.CLICK: "Input.synthesizeTapGesture",
        ActionType.GET_ELEMENT_RECT: "Runtime.evaluate",
        ActionType.GET_PICKER_RECT: "Runtime.evaluate",
        ActionType.GET_ELEMENT_TEXT: "Runtime.evaluate",
        ActionType.GET_ELEMENT_SRC: "Runtime.evaluate",
        ActionType.GET_PAGE_HEIGHT: "Runtime.evaluate",
        ActionType.GET_JS_VALUE: "Runtime.evaluate",
        ActionType.TEXT: "Input.dispatchKeyEvent",
        ActionType.IS_ELEMENT_EXIST: "Runtime.evaluate",
        ActionType.GET_WINDOW_HEIGHT: "Runtime.evaluate",
        ActionType.GET_WINDOW_WIDTH: "Runtime.evaluate"

    }

    # string.Template
    # jsonConcat最终拼接的模板
    _paramsMap = {
        "Runtime.evaluate": '{"expression": "$expression"}',
        "Input.synthesizeScrollGesture":
            '{"type": "mouseWheel", "x": $x, "y": $y,"xDistance": $xDistance, "yDistance": $yDistance,"speed":$speed}',
        "Page.navigate": '{"url":"$url"}',
        "Input.dispatchKeyEvent": '{"type":"$type","text":"$text","unmodifiedText":"$text"}',
        "Input.synthesizeTapGesture": '{"x":$x,"y":$y}',
        "DOM.getDocument": "{''}",
        "DOM.getOuterHTML": '{"nodeId": $nodeId}',
    }

    # doCommandWithoutElement 中执行的参数
    _expressionMap = {
        ActionType.GET_PAGE_HEIGHT: 'document.body.scrollHeight',
        ActionType.GET_JS_VALUE: '$value',
        ActionType.GET_WINDOW_HEIGHT: 'document.documentElement.clientHeight',
        ActionType.GET_WINDOW_WIDTH: "document.documentElement.clientWidth"

    }

    def getElement(self, actionType, default=None):
        return self._elementMap.get(actionType, default)

    def getJsAction(self, actionType, default=None):
        return self._jsActionMap.get(actionType, default)

    def getMethod(self, actionType, default=None):
        return self._methodMap.get(actionType, default)

    def getParams(self, actionType, default=None):
        return self._paramsMap.get(actionType, default)

    def getExpression(self, actionType, default=None):
        return self._expressionMap.get(actionType, default)
