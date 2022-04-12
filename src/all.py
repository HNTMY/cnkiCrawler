# common
from commontools import *
from cnkiManager import *
from crawler_log import *
from runThreads import *

if __name__ == '__main__':
    LOGI('main thread start')
    carriers = ['qk', 'hy']
    numpre = int(sys.argv[1])
    if not numpre:
        LOGE('参数错误')
        sys.exit(-1)

    sem.init(numpre)
    threads = []
    for carrier in carriers:
        threads += crawlerEnter(carrier)
        LOGD('len_threads: {}'.format(len(threads)))

    indexList = [i for i in range(len(threads))]
    startList = [0 for i in range(len(threads))]
    runthreads = runThreads(threads, indexList, startList)
    runthreads.run()

    LOGI('main thread end')