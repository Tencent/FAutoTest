# -*- coding: utf-8 -*-
from fastAutoTest.core.common.command.commandProcessor import CommandProcessor
from fastAutoTest.core.wx import wxUserAPI


class WxPageOperator(object):
    processor = CommandProcessor('wx')

    def clickElementByXpath(self, x, y):
        params = {"x": x, "y": y}
        return self.processor.doCommandWithoutElement(wxUserAPI.ActionType.CLICK, **params)

    def getJSValue(self, value):
        params = {"value": value}
        return self.processor.doCommandWithoutElement(wxUserAPI.ActionType.GET_JS_VALUE, **params)

    def getElementRect(self, xpath):
        params = {"xpath": xpath}
        return self.processor.doCommandWithElement(wxUserAPI.ByType.XPATH, wxUserAPI.ActionType.GET_ELEMENT_RECT,
                                                   **params)

    def returnLastPage(self):
        return self.processor.doCommandWithoutElement(wxUserAPI.ActionType.RETURN_LAST_PAGE)

    def getPageHeight(self):
        return self.processor.doCommandWithoutElement(
            wxUserAPI.ActionType.GET_PAGE_HEIGHT)

    def isElementExist(self, xpath):
        params = {"xpath": xpath}
        return self.processor.doCommandWithElement(wxUserAPI.ByType.XPATH, wxUserAPI.ActionType.IS_ELEMENT_EXIST,
                                                   **params)

    def getElementTextByXpath(self, xpath):
        params = {"xpath": xpath}
        return self.processor.doCommandWithElement(wxUserAPI.ByType.XPATH, wxUserAPI.ActionType.GET_ELEMENT_TEXT,
                                                   **params)

    def getElementSrcByXpath(self, xpath):
        params = {"xpath": xpath}
        return self.processor.doCommandWithElement(wxUserAPI.ByType.XPATH, wxUserAPI.ActionType.GET_ELEMENT_SRC,
                                                   **params)

    def scrollWindow(self, x, y, xDistance, yDistance, speed=800):
        params = {"x": x, "y": y, "xDistance": xDistance, "yDistance": yDistance, "speed": speed}
        return self.processor.doCommandWithoutElement(wxUserAPI.ActionType.SCROLL, **params)

    def getWindowHeight(self):
        return self.processor.doCommandWithoutElement(wxUserAPI.ActionType.GET_WINDOW_HEIGHT)

    def getWindowWidth(self):
        return self.processor.doCommandWithoutElement(wxUserAPI.ActionType.GET_WINDOW_WIDTH)

    def getDocument(self):
        return self.processor.doCommandWithoutElement(
            wxUserAPI.ActionType.GET_DOCUMENT)

    def getHtml(self, nodeId):
        params = {"nodeId": nodeId}
        return self.processor.doCommandWithoutElement(
            wxUserAPI.ActionType.GET_HTML, **params)

    def changeDp2Px(self, xDp, yDp, scale, appTitleHeight):
        xPx = int(xDp * scale + 0.5)
        yPx = int((yDp + appTitleHeight) * scale + 0.5)
        return xPx, yPx
