# -*- coding: utf-8 -*-

import os

from commandHelper import runCommand


class AdbHelper:
    def __init__(self):
        pass

    @staticmethod
    def specifyDeviceOnCmd(cmd, device):
        return cmd if device is None else cmd.replace("adb", "adb -s %s" % device)

    @staticmethod
    def listDevices(ignoreUnconnectedDevices=True, printDetails=False, cwd=None):
        import re

        devicesList = []
        cmd = "adb devices"
        stdoutData, stderrorData = runCommand(cmd, printDetails=printDetails, cwd=cwd)
        lines = stdoutData.split(os.linesep)
        pattern = re.compile(r"\b(device|offline|emulator|host|unauthorized)\b")
        for line in lines:
            if pattern.findall(line):
                name, status = line.replace("\t", " ").strip().split()
                if ignoreUnconnectedDevices and status == "device":
                    devicesList.append(name)
                else:
                    devicesList.append(name)

        return devicesList

    @staticmethod
    def screenOn(device=None, printDetails=False, cwd=None):
        cmd = "adb shell input keyevent 224"
        if device:
            cmd = cmd.replace("adb", "adb -s %s" % device)

        return runCommand(cmd, printDetails=printDetails, cwd=cwd)

    @staticmethod
    def unLockScreen(device=None, fromX=None, fromY=None, toX=None, toY=None, printDetails=False, cwd=None):

        if not fromX:
            fromX = 300

        if not fromY:
            fromY = 1000

        if not toX:
            toX = 300

        if not toY:
            toY = 500

        cmd = "adb shell input swipe %s %s %s %s" % (
            fromX,
            fromY,
            toX,
            toY)

        if device:
            cmd = cmd.replace("adb", "adb -s %s" % device)

        return runCommand(cmd, printDetails=printDetails, cwd=cwd)

    @staticmethod
    def runInstrumentationTestForWholePackage(pkgName, device=None, runnerName=None, printDetails=False, cwd=None):
        if not runnerName:
            runnerName = "android.support.test.runner.AndroidJUnitRunner"

        cmd = "adb shell am instrument -w -r -e package %s -e debug false %s.test/%s" % (
            pkgName,
            pkgName,
            runnerName)

        if device:
            cmd = cmd.replace("adb", "adb -s %s" % device)

        return runCommand(cmd, printDetails=printDetails, cwd=cwd)

    @staticmethod
    def runInstrumentationTestForClass(pkgName, testcaseName, device=None,
                                       runnerName=None, printDetails=False, cwd=None):
        if not runnerName:
            runnerName = "android.support.test.runner.AndroidJUnitRunner"

        cmd = "adb shell am instrument -w -r -e debug false -e class %s.%s %s.test/%s" % (
            pkgName,
            testcaseName,
            pkgName,
            runnerName)

        if device:
            cmd = cmd.replace("adb", "adb -s %s" % device)

        return runCommand(cmd, printDetails=printDetails, cwd=cwd)

    @staticmethod
    def installApk(apkFile, device=None, installOverride=False, printDetails=False, cwd=None):
        cmd = "adb install {0}"

        if device:
            cmd = cmd.replace("adb", "adb -s %s" % device)

        if installOverride:
            cmd = cmd.replace("install", "install -r")

        return runCommand(cmd.format(apkFile), printDetails=printDetails, cwd=cwd)

    @staticmethod
    def hasApkInstalled(packageName='com.tencent.fat.wxinputplug', device=None):
        ADB_FIND_PACKAGE_CMD = 'adb shell pm list packages'
        if device:
            ADB_FIND_PACKAGE_CMD = ADB_FIND_PACKAGE_CMD.replace("adb", "adb -s %s" % device)
        stdout, stdError = runCommand(AdbHelper.specifyDeviceOnCmd(ADB_FIND_PACKAGE_CMD, device))
        return packageName in stdout


if __name__ == "__main__":
    pass
