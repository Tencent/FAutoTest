# -*- coding: utf-8 -*-


class ByType(object):
    ID = "id"
    NAME = "name"
    XPATH = "xpath"


class ActionType(object):
    CLICK = "click"
    TEXT = "text"
    SCROLL = "scroll"
    GET_DOCUMENT = "getDocument"
    GET_HTML = "getHTML"
    RETURN_LAST_PAGE = "returnPage"
    CLOSE_WINDOW = "closeWindow"
    GET_PICKER_RECT = "getRect"
    GET_JS_VALUE = "getJsValue"
    GET_ELEMENT_TEXT = "getElementText"
    GET_ELEMENT_SRC = "getElementSrc"
    GET_ELEMENT_CLASS_NAME = "getElementClassName"
    IS_ELEMENT_EXIST = 'isElementExist'
    NAVIGATE_PAGE = 'navigatePage'
    GET_PAGE_HEIGHT = 'getPageHeight'
    EXECUTE_SCRIPT = 'executeScript'
    FOCUS = 'focus'
    GET_ELEMENT_RECT = 'getElementRect'
    GET_WINDOW_HEIGHT = 'getWindowHeight'
    GET_WINDOW_WIDTH = 'getWindowWidth'
    CLEAR_INPUT_TEXT = 'clearInputText'
    GET_PAGE_URL = 'getPageUrl'
    GET_ALL_CONTEXT = 'getAllContext'
    GET_BODY_NODE = 'getBodyNode'
    REQUEST_CHILD_NODES = 'requestChildNodes'
