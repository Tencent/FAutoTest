# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
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
