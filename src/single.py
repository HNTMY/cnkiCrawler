# common
from commontools import *
from cnkiManager import *
from crawler_log import *

if __name__ == '__main__':
    LOGI('main thread start')
    clas = int(sys.argv[1])
    index = int(sys.argv[2])
    if clas == None or index == None:
        LOGE('参数错误')
        sys.exit(-1)
    carriers = ['xsqk', 'hy']
    # 获取高级检索文献分类数
    sem.init(1)
    list = crawlerEnter(carriers[clas], index)
    list[0].start()
    list[0].join()
    LOGI('main thread end')