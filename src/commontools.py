# common
import threading
# selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

class Sem():
    def __init__(self, num = 2):
        self.sem = threading.Semaphore(value = num)
        self.flag = False
    def init(self, num):
        if not self.flag:
            self.sem = threading.Semaphore(value = num)
            self.flag = True
    def acquire(self):
        self.sem.acquire()
    def release(self):
        self.sem.release()
sem = Sem()

def getChromeDriver(options):
    opts = webdriver.ChromeOptions()
    for opt in options:
        opts.add_argument(opt)
    driver = webdriver.Chrome(options = opts)
    return driver

def isElementPresent(driver, by, value):
        """
        用来判断元素标签是否存在，
        """
        try:
            driver.find_element(by=by, value=value)
        # 原文是except NoSuchElementException, e:
        except NoSuchElementException as e:
            # 发生了NoSuchElementException异常，说明页面中未找到该元素，返回False
            return False
        else:
            # 没有发生异常，表示在页面中找到了该元素，返回True
            return True

# 点击元素并打开新标签页
def clickOpenWindow(driver, element, index, by, value):
    driver.switch_to.window(index)
    element.find_element(by, value).click()
    newWindow= driver.window_handles[len(driver.window_handles)-1]
    return newWindow