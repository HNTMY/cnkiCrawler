from cnkiManager import *

class runThreads():
    def __init__(self, threads, start = 0, end = None):
        self.threads = threads
        self.count = len(threads)
        self.start = start
        if end is None:
            self.end = len(self.count)
        else:
            self.end = end
        # self.numpre = numpre
        # self.sem = threading.Semaphore(numpre)
    def run(self):
        for i in range(self.start, self.end):
            self.threads[i].start()
        for i in range(self.start, self.end):
            self.threads[i].join()
        # self.sem.acquire()
        # tmpThreads = []
        # for i in range(self.numpre):
        #     if self.count:
        #         tmpThreads.append(self.threads.pop())
        #         self.count -= 1
        # for tmpThread in tmpThreads:
        #     tmpThread.start()
        # for tmpThread in tmpThreads:
        #     tmpThread.join()
        # self.sem.release()
            