# -*- coding: utf-8 -*-
'''
Tencent is pleased to support the open source community by making FAutoTest available.
Copyright (C) 2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the BSD 3-Clause License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

'''
import Queue
import threading

from atomicinteger import AtomicInteger

__all__ = [
    "SingleThreadExecutor"
]


class _WorkerThread(threading.Thread):
    ID = AtomicInteger(initValue=0)

    def __init__(self, queue):
        super(_WorkerThread, self).__init__(name="_WorkerThread_%s" % _WorkerThread.ID.getAndIncrement())
        self._queue = queue
        self._quit = False

    def run(self):
        while not self._quit:
            try:
                inParam = self._queue.get(block=True)
                if inParam == self:
                    # self means quit
                    break

                callbackFunc, args, kwargs = inParam
                if callable(callbackFunc):
                    callbackFunc(*args, **kwargs)
                self._queue.task_done()
            except Exception as e:
                print(e.message)
                raise

    def quit(self):
        if not self._quit:
            self._queue.put(self)
            self._quit = True

    def isQuit(self):
        return self._quit


class SingleThreadExecutor(object):
    def __init__(self):
        self._queue = Queue.Queue()
        self._workerThread = _WorkerThread(self._queue)
        self._workerThread.setDaemon(True)
        self._workerThread.start()

    def put(self, func, *args, **kwargs):
        if self._workerThread.isQuit():
            raise RuntimeError("executor is quit")

        self._queue.put((func, args, kwargs))

    def shutDownNow(self):
        self._workerThread.quit()

    def shutDown(self):
        self._queue.join()
        self.shutDownNow()
        self._workerThread.join()


if __name__ == "__main__":
    pass
