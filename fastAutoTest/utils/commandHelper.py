# -*- coding: utf-8 -*-

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
