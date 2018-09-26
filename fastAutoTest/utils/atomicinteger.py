# -*- coding: utf-8 -*-

from threading import Lock


class AtomicInteger(object):

    def __init__(self, initValue=0):
        self._initValue = initValue
        self._lock = Lock()

    def getAndIncrement(self):
        with self._lock:
            tmp = self._initValue
            self._initValue += 1
            return tmp

    def incrementAndGet(self):
        with self._lock:
            self._initValue += 1
            return self._initValue

    def getAndDecrement(self):
        with self._lock:
            tmp = self._initValue
            self._initValue -= 1
            return tmp

    def decrementAndGet(self):
        with self._lock:
            self._initValue -= 1
            return self._initValue
