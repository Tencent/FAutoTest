# -*- coding: utf-8 -*-

import threading

from websocket import create_connection

__all__ = [
    "WebSocketDataTransfer",
    "DataTransferCallback"
]


class DataTransferCallback(object):
    def onMessage(self, message):
        pass


class WebSocketDataTransfer(object):
    def __init__(self, url):
        self._url = url
        self._callbacks = []
        self._webSocket = None
        self._isConnected = False
        self._lock = threading.Lock()

    def setUrl(self, url):
        self._url = url

    def getUrl(self):
        return self._url

    def connect(self):
        if not self._isConnected:
            self._webSocket = create_connection(url=self._url)
            self._isConnected = True

    def disconnect(self):
        self._webSocket.close()
        self._isConnected = False

    def send(self, data):
        self._webSocket.send(data)

    def receive(self):
        message = self._webSocket.recv()
        self._onMessage(message)

    def isConnected(self):
        return self._isConnected

    def registerCallback(self, callback):
        if not isinstance(callback, DataTransferCallback):
            raise RuntimeError("call back must be DataTransferCallback sub class")

        with self._lock:
            self._callbacks.append(callback)

    def unregisterCallback(self, callback):
        if not isinstance(callback, DataTransferCallback):
            raise RuntimeError("call back must be DataTransferCallback sub class")
        with self._lock:
            self._callbacks.remove(callback)

    def _onMessage(self, message):
        with self._lock:
            for callback in self._callbacks:
                callback.onMessage(message)


class TestCallback(DataTransferCallback):
    def onMessage(self, message):
        print("onMessage --> " + message)


if __name__ == "__main__":
    pass
