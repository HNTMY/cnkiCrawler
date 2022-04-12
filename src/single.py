# common
from commontools import *
from cnkiManager import *
from crawler_log import *
from runThreads import *

if __name__ == '__main__':
    LOGI('main thread start')
    carriers = ['qk', 'hy']
    numpre = int(sys.argv[1])
    index = sys.argv[2]
    startIndex = sys.argv[3]
    if numpre is None or index is None or startIndex is None:
        print('参数错误')
        sys.exit(-1)
    print(numpre, index, startIndex)
    indexList = [int(i) for i in index.strip('[]').split(',')]
    startList = [int(i) for i in startIndex.strip('[]').split(',')]
    print(indexList, startList)
    sem.init(numpre)
    threads = []
    for carrier in carriers:
        threads += crawlerEnter(carrier)
        LOGD('len_threads: {}'.format(len(threads)))

    runthreads = runThreads(threads, indexList, startList)
    runthreads.run()
    LOGI('main thread end')