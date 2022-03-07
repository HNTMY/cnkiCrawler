import sys
import time

# foreground color
FORE_BLACK = 30
FORE_RED = 31
FORE_GREEN = 32
FORE_YELLOW = 33
FORE_BLUE = 34
FORE_WHITE = 37

# background color
BACK_BLACK = 40
BACK_RED = 41
BACK_GREEN = 42
BACK_YELLOW = 43
BACK_BLUE = 44
BACK_WHITE = 47

def get_cur_info():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        f = sys.exc_info()[2].tb_frame.f_back
    return (f.f_code.co_name, f.f_lineno)

def LOGI(*args, **kwargs):
    color = FORE_GREEN
    tm = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print('\033[' + str(color) + 'm', end = '')
    print('[' + str(tm) + '] ', end = '')
    print(*args, end = '')
    print('\033[0m', **kwargs)

def LOGD(*args, **kwargs):
    color = FORE_WHITE
    tm = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print('\033[' + str(color) + 'm', end = '')
    print('[' + str(tm) + '] ', end = '')
    print(*args, end = '')
    print('\033[0m', **kwargs)

def LOGW(*args, **kwargs):
    color = FORE_YELLOW
    tm = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print('\033[' + str(color) + 'm', end = '')
    print('[' + str(tm) + '] ', end = '')
    print(*args, end = '')
    print('\033[0m', **kwargs)

def LOGE(*args, **kwargs):
    color = FORE_RED
    tm = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print('\033[' + str(color) + 'm', end = '')
    print('[' + str(tm) + '] ', end = '')
    print(*args, end = '')
    print('\033[0m', **kwargs)