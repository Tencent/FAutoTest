# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
from fastAutoTest.core.h5.h5UserAPI import ActionType
from fastAutoTest.core.h5.h5UserAPI import ByType


class H5CommandManager(object):
    # 使用$$可以作为格式化时的转义
    _elementMap = {
        ByType.ID: "$$('#$id')[0]",
        ByType.NAME: "$$('.$name')[$index]",
        ByType.XPATH: "var xpath ='$xpath';"
                      "xpath_obj = document.evaluate(xpath,document,null, XPathResult.ANY_TYPE, null);"
                      "var button = xpath_obj.iterateNext()"
    }

    _methodMap = {
        ActionType.GET_DOCUMENT: "DOM.getDocument",
        ActionType.GET_HTML: "DOM.getOuterHTML",
        ActionType.SCROLL: "Input.synthesizeScrollGesture",
        ActionType.CLICK: "Input.synthesizeTapGesture",
        ActionType.FOCUS: "Runtime.evaluate",
        ActionType.RETURN_LAST_PAGE: "Runtime.evaluate",
        ActionType.CLOSE_WINDOW: "Runtime.evaluate",
        ActionType.GET_PICKER_RECT: "Runtime.evaluate",
        ActionType.GET_JS_VALUE: "Runtime.evaluate",
        ActionType.GET_ELEMENT_TEXT: "Runtime.evaluate",
        ActionType.GET_ELEMENT_SRC: "Runtime.evaluate",
        ActionType.GET_ELEMENT_CLASS_NAME: "Runtime.evaluate",
        ActionType.IS_ELEMENT_EXIST: "Runtime.evaluate",
        ActionType.NAVIGATE_PAGE: "Page.navigate",
        ActionType.GET_PAGE_HEIGHT: "Runtime.evaluate",
        ActionType.EXECUTE_SCRIPT: "Runtime.evaluate",
        ActionType.TEXT: "Input.dispatchKeyEvent",
        ActionType.GET_ELEMENT_RECT: "Runtime.evaluate",
        ActionType.GET_WINDOW_HEIGHT: "Runtime.evaluate",
        ActionType.GET_WINDOW_WIDTH: "Runtime.evaluate",
        ActionType.CLEAR_INPUT_TEXT: "Runtime.evaluate",
        ActionType.GET_PAGE_URL: "Runtime.evaluate",
        ActionType.GET_ALL_CONTEXT: "Runtime.enable",
        ActionType.GET_BODY_NODE: "DOM.requestChildNodes",
        ActionType.REQUEST_CHILD_NODES: "DOM.requestChildNodes"

    }

    # doCommandWithElement中执行的参数
    _jsActionMap = {
        ActionType.FOCUS: ";button.focus();",
        ActionType.GET_PICKER_RECT: ";var parent = button.parentElement;"
                                    "var pparent = parent.parentElement;"
                                    "var count = parent.childElementCount;"
                                    "for(var i = 0;i<count;i++)"
                                    "{if(button == parent.childNodes[i])"
                                    "{var index = i}};"
                                    "bound = parent.getBoundingClientRect();"
                                    "height = bound.height;"
                                    "per_item_height = height/count;"
                                    "dex = per_item_height * index;"
                                    "start_scroll_x = bound.left + 5;"
                                    "start_scroll_y = pparent.getBoundingClientRect().top+20;",
        ActionType.GET_ELEMENT_TEXT: ";button.innerText;",
        ActionType.GET_ELEMENT_SRC: ";button.src;",
        ActionType.GET_ELEMENT_CLASS_NAME: ";button.className;",
        ActionType.IS_ELEMENT_EXIST: ";button;",
        ActionType.GET_ELEMENT_RECT: ";left=Math.round(button.getBoundingClientRect().left);"
                                     "right=Math.round(button.getBoundingClientRect().right);"
                                     "bottom=Math.round(button.getBoundingClientRect().bottom);"
                                     "topp=Math.round(button.getBoundingClientRect().top);"
                                     "x=Math.round((left+right)/2);"
                                     "y=Math.round((topp+bottom)/2);",
        ActionType.CLEAR_INPUT_TEXT: ";button.value=''",
    }

    # doCommandWithoutElement 中执行的参数
    _expressionMap = {
        ActionType.RETURN_LAST_PAGE: 'history.back()',
        ActionType.CLOSE_WINDOW: "WeixinJSBridge.call('closeWindow')",
        ActionType.GET_JS_VALUE: '$value',
        ActionType.GET_PAGE_HEIGHT: 'document.body.scrollHeight',
        ActionType.EXECUTE_SCRIPT: '$script',
        ActionType.GET_WINDOW_HEIGHT: 'document.documentElement.clientHeight',
        ActionType.GET_WINDOW_WIDTH: "document.documentElement.clientWidth",
        ActionType.GET_PAGE_URL: "window.location.href"
    }

    # string.Template
    # 用在jsonConcat的格式化中
    _paramsMap = {
        "Runtime.evaluate": '{"expression": "$expression"}',
        "DOM.getDocument": "{''}",
        "DOM.getOuterHTML": '{"nodeId": $nodeId}',
        "Input.synthesizeScrollGesture":
            '{"type": "mouseWheel", "x": $x, "y": $y,"xDistance": $xDistance, "yDistance": $yDistance,"speed":$speed}',
        "Page.navigate": '{"url":"$url"}',
        "Input.dispatchKeyEvent": '{"type":"$type","text":"$text"}',
        "Input.synthesizeTapGesture": '{"x":$x,"y":$y,"duration":$duration,"tapCount":$tapCount}',
        "Runtime.enable": "{''}",
        "DOM.requestChildNodes": '{"nodeId":$nodeId,"pierce":true,"depth":-1}'

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


if __name__ == "__main__":
    pass
