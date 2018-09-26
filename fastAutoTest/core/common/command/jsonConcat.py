# -*- coding: utf-8 -*-
import json
import string

from fastAutoTest.core.h5 import h5CommandManager
from fastAutoTest.core.wx import wxCommandManager


class JsonConcat(object):
    def __init__(self, managerType):
        if managerType == "h5":
            self.manager = h5CommandManager.H5CommandManager()
        else:
            self.manager = wxCommandManager.WxCommandManager()

    def concat(self, action_type, **params):
        method = self.manager.getMethod(action_type, None)
        if len(params) != 0:
            paramsTemplate = self.manager.getParams(method)
            paramsCat = string.Template(paramsTemplate)
            paramsResult = paramsCat.substitute(**params)
            paramsResult = json.loads(paramsResult)

            # print json.dumps(params_result)
        else:
            # 有getDocument这些不需要参数的情况
            paramsResult = "{}"
        result = dict()
        result['method'] = method
        result['params'] = paramsResult
        jsonResult = json.dumps(result)
        return jsonResult
