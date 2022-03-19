import inspect
from crawler_log import *

def f2():
    print(inspect.stack()[1])
    print('{}\n{}\n{}'.format(inspect.stack()[1][0], inspect.stack()[1][2], inspect.stack()[1][1]))

def main():
    LOGI()

main()