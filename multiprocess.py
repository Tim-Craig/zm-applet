from multiprocessing import Process, Queue
import time


class Foo(object):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


class Worker(object):
    def __init__(self):
        self.queue = Queue()

    def do_work(self):
        for i in range(10):
            p = Process(target=self.run, args=(i,))
            p.start()
        val = self.queue.get(block=True)
        while val:
            print val.a, val.b,val.c
            val = self.queue.get(block=True)

    def run(self, i):
        time.sleep(10)
        self.queue.put(Foo(i,i,i))


if __name__ == '__main__':
    worker = Worker()
    worker.do_work()
