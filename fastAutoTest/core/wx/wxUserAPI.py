# -*- coding: utf-8 -*-


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
