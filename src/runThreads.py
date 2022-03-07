from cnkiManager import *

class runThreads():
    def __init__(self, threads):
        self.threads = threads
        self.count = len(threads)
    def run(self):
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()
            # tmpThreads = []
            # for i in range(self.numpre):
            #     if self.count:
            #         tmpThreads.append(self.threads.pop())
            #         self.count -= 1
            # for tmpThread in tmpThreads:
            #     tmpThread.start()
            # for tmpThread in tmpThreads:
            #     tmpThread.join()
            