# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
import subprocess

from fastAutoTest.core.common.errormsgmanager import *


def runCommand(cmd, printDetails=False, cwd=None):
    p = subprocess.Popen(cmd, cwd=cwd,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stdError = p.communicate()
    if printDetails:
        print("runCommand --> " + stdout)

    if printDetails and stdError:
        print(stdError)

    if p.returncode != 0:
        errorMsg = ErrorMsgManager().errorCodeToString(ERROR_CODE_NOT_CONFIG_ENV)
        raise RuntimeError("%s, %s" % (cmd, errorMsg))

    return stdout, stdError


if __name__ == "__main__":
    cmd = "adb forward tcp:%s localabstract:webview_devtools_remote_%s" % (9222, 123)
    out, error = runCommand(cmd)
    print(error == "")
    print out
