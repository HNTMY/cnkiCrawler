from cnkiManager import *

class runThreads():
    def __init__(self, threads, indexList, startList):
        self.threads = threads
        self.count = len(threads)
        self.indexList = indexList
        self.startList = startList
        # self.numpre = numpre
        # self.sem = threading.Semaphore(numpre)
    def run(self):
        LOGI(self.indexList)
        LOGI(self.startList)
        for i in range(len(self.indexList)):
            self.threads[self.indexList[i]].setStart(self.startList[i])
            self.threads[self.indexList[i]].start()
        for i in self.indexList:
            LOGI('join {}'.format(i))
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
            