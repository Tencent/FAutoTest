# -*- coding: utf-8 -*-

import platform


class FuncHelper(object):
    @staticmethod
    def isCallable(obj):
        return obj is not None and hasattr(obj, '__call__')


class DictHelper(object):
    @staticmethod
    def getValue(dict, key, defaultValue=None):
        if key in dict:
            return dict[key]
        else:
            return defaultValue


class OS(object):
    @staticmethod
    def getPlatform():
        return platform.system()


if __name__ == "__main__":
    pass
