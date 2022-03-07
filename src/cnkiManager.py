from typing import final
from commontools import *
import threading
import time
from crawler_log import *
from mongoDBManager import *
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

cnkiUrl = 'https://www.cnki.net/'   # 知网主页url
xsqkNum = 50                        # 单个文献分类学术期刊最大爬取数量
hyNum = 50                          # 单个文献分类会议最大爬取数量

timeOutTotal = 10                   # 超时等待总时间
perTime = 1                         # 轮询时间

xsqkDB = 'xsqk'               # 学术期刊数据库名
hyDB = 'hy'                   # 会议数据库名

cnPercent = 0.3               # 标题中中文所占比例阈值

# 学术期刊
xsqkInfoCSS = {
    'qk_name': r'div.top-tip > span > a',        # 所属期刊名称及时间(可能没有时间)
    'qk_netTime': r'div.head-time > span',       # 文献网络首发时间
    'qk_title': r'div.wx-tit > h1',              # 文献标题
    'qk_auther': r'h3#authorpart.author > span', # 作者
    'qk_institution': r'a.author',               # 作者所属机构
    'qk_abstract': r'span#ChDivSummary',         # 摘要
    'qk_keys': r'p.keywords > a'                 # 关键字
}
# 会议
hyInfoCSS = {
    'hy_title': r'div.wx-tit > h1',              # 文献标题
    'hy_auther': r'h3#authorpart.author > span', # 作者
    'hy_institution': r'a.author',               # 作者所属机构
    'hy_abstract': r'span#ChDivSummary',         # 摘要
    'hy_keys': r'p.keywords > a'                 # 关键字
}
hy_info = r'div.row > span'                      # 会议信息（名称、时间、地点等）

# 获取一个driver实例并打开知网高级检索>文献分类
def openWxfl(carrier):
    options = [
        '--disable-gpu',
        '--blink-settings=imagesEnabled=false',
        '--headless',
        # '--disk-cache-dir=/tmp/google-chrome',
        ]
    driver = getChromeDriver(options)

    driver.get(cnkiUrl)
    homePage = driver.current_window_handle

    highSearch = clickOpenWindow(driver, driver, homePage, By.ID, 'highSearch')
    driver.close()
    driver.switch_to.window(highSearch)
    
    timeout = 0
    timeoutFlag = False
    while True:
        try:
            if timeout >= timeOutTotal:
                timeoutFlag = True
                break
            if carrier == 'xsqk':
                # 点击学术期刊，中文，SCI来源
                WebDriverWait(driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-id="xsqk"]')))
                driver.find_element(by = By.CSS_SELECTOR, value = 'li[data-id="xsqk"]').click()
                WebDriverWait(driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.ch')))
                driver.find_element(by = By.CSS_SELECTOR, value = 'a.ch').click()
                WebDriverWait(driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[key="SI"]')))
                driver.find_element(by = By.CSS_SELECTOR, value = 'input[key="SI"]').click()
                break
            elif carrier == 'hy':
                # 点击会议，语种选择中文
                WebDriverWait(driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-id="hy"]')))
                driver.find_element(by = By.CSS_SELECTOR, value = 'li[data-id="hy"]').click()
                WebDriverWait(driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-title="语种"]')))
                driver.find_element(by = By.CSS_SELECTOR, value = 'div[data-title="语种"]').click()
                driver.find_elements(by = By.CSS_SELECTOR, value = 'div[data-title="语种"]>div>ul>li')[1].click()
                break
            else:
                driver.quit()
                return None
        except:
            LOGI('select carrier error, try again')
            time.sleep(2)
            driver.refresh()
            time.sleep(perTime)
            timeout += perTime
    if timeoutFlag:
        LOGE('select carrier error, quit')
        return None
    # 点击文献分类
    driver.find_element(by = By.CSS_SELECTOR, value = 'a.icon-arrow').click()
    return driver

'''
    创建爬虫线程
'''
def crawlerEnter(carrier, index = None):
    driver = openWxfl(carrier)
    if not driver:
        LOGE('openWxfl error {}'.format('crawlerEnter'))
        return None
    wxfl = driver.find_element(by = By.CSS_SELECTOR, value = 'ul#defult.nav-content-list')
    list = wxfl.find_elements(by = By.CSS_SELECTOR, value = 'li')
    wxflNum = len(list)
    LOGI(wxflNum)
    classes = []
    for i in range(wxflNum):
        classes.append(list[i].text)
    driver.quit()

    '''
        多线程爬取文献数据
        共分为wxflNum个线程，每个线程创建一个webdriver实例
    '''
    threads_list = []
    # 创建线程
    db = getDB(carrier)
    if index != None:
        db.summary.delete_one({'id': index})
        insertDict = {}
        insertDict['id'] = index
        insertDict['class'] = classes[index]
        insertDict['count'] = 0
        db.summary.insert_one(insertDict)
        db[classes[index]].drop()
        tmp_thread = crawler(carrier, index)
        tmp_thread.init()
        LOGI('{}.{}'.format(carrier, index))
        threads_list.append(tmp_thread)
    else:
        db.summary.delete_many({})
        for i in range(wxflNum):
            insertDict = {}
            insertDict['id'] = i
            insertDict['class'] = classes[i]
            insertDict['count'] = 0
            db.summary.insert_one(insertDict)
            db[classes[i]].drop()
            tmp_thread = crawler(carrier, i)
            tmp_thread.init()
            LOGI('{}.{}'.format(carrier, i))
            threads_list.append(tmp_thread)
    return threads_list

def processResult(crawler):
    driver = crawler.driver
    newHighSearch = crawler.pageId
    carrier = crawler.carrier
    cnt = 0
    driver.switch_to.window(newHighSearch)
    maxNum = 0
    currentWindowsNum = len(driver.window_handles)
    if(carrier == 'xsqk'):
        maxNum = xsqkNum
    elif(carrier == 'hy'):
        maxNum = hyNum
    if isElementPresent(driver, By.CSS_SELECTOR, 'table.result-table-list>tbody'):
        while True:
            flag = False
            try:
                tbody = driver.find_element(by = By.CSS_SELECTOR, value = 'table.result-table-list>tbody')
                articles = tbody.find_elements(by = By.XPATH, value = './*')
            except:
                continue
            saves = []
            title = ''
            for article in articles:
                newTab = ''
                try:
                    WebDriverWait(article, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'td.name>a')))
                    art = article.find_element(by = By.CSS_SELECTOR, value = 'td.name>a')
                    art.click()
                    title = art.text
                except StaleElementReferenceException:
                    flag = True
                    break
                except ElementClickInterceptedException:
                    LOGI('ElementClickInterceptedException')
                    time.sleep(2)
                    continue
                except TimeoutException:
                    LOGI('TimeoutException')
                    continue
                except Exception:
                    flag = True
                    break
                cnNum = 0
                totalNum = len(title)
                for char in title:
                    if char >= '\u4e00' and char <= '\u9fa5':
                        cnNum += 1
                if(cnNum/totalNum < cnPercent):
                    if len(driver.window_handles) != currentWindowsNum:
                        newTab = driver.window_handles[len(driver.window_handles)-1]
                        driver.switch_to.window(newTab)
                        driver.close()
                        driver.switch_to.window(newHighSearch)
                    continue
                LOGI(title)
                LOGD('driver handles size:', len(driver.window_handles))
                if len(driver.window_handles) == currentWindowsNum:
                    LOGI('window count: {}'.format(len(driver.window_handles)))
                    LOGI(driver.window_handles, newHighSearch)
                    continue
                try:
                    newTab = driver.window_handles[len(driver.window_handles)-1]
                    driver.switch_to.window(newTab)
                    if(carrier == 'xsqk'):
                        save = xsqkResult(driver)
                        if save != None:
                            saves.append(save)
                            cnt = cnt + 1
                    elif(carrier == 'hy'):
                        save = hyResult(driver)
                        if save != None:
                            saves.append(save)
                            cnt = cnt + 1
                except Exception as e:
                    print(e, 'save article info error, next')
                finally:
                    driver.close()
                    driver.switch_to.window(newHighSearch)
                    LOGD('driver handles size:', len(driver.window_handles))
                if cnt >= maxNum:
                    break
            if flag:
                continue
            if len(saves) > 0:
                collection = getCollection(crawler.carrier, crawler.wxfl)
                collection.insert_many(saves)
            if cnt >= maxNum:
                break
            if(isElementPresent(driver, By.CSS_SELECTOR, 'a#PageNext')):
                while True:
                    try:
                        nextPage = driver.find_element(by = By.CSS_SELECTOR, value = 'a#PageNext')
                        nextPage.click()
                    except:
                        LOGE('next page click failed, try again')
                    else:
                        break
            else:
                break
    return cnt

def xsqkResult(driver):
    # 学术期刊
    save = {}
    timeout = 0
    while True:
        try:
            if timeout >= timeOutTotal:
                return None
            moreEle = driver.find_element(by = By.CSS_SELECTOR, value = 'a#ChDivSummaryMore')
            break
        except:
            time.sleep(perTime)
            timeout += perTime
            continue
    if(moreEle.get_attribute('style') != 'display: none;'):
        timeout = 0
        while True:
            try:
                if timeout >= timeOutTotal:
                    return None
                driver.execute_script('arguments[0].click()', moreEle)
                break
            except Exception as e:
                print(e, 'click more error, again')
                time.sleep(perTime)
                timeout += perTime
                continue
    for css in xsqkInfoCSS:
        if isElementPresent(driver, By.CSS_SELECTOR, xsqkInfoCSS[css]):
            eles = driver.find_elements(by = By.CSS_SELECTOR, value = xsqkInfoCSS[css])
            infoStr = ''
            for ele in eles:
                infoStr += ele.text
                infoStr += '  '
            save[css] = infoStr
    return save

def hyResult(driver):
    # 会议
    save = {}
    timeout = 0
    while True:
        try:
            if timeout >= timeOutTotal:
                return None
            moreEle = driver.find_element(by = By.CSS_SELECTOR, value = 'a#ChDivSummaryMore')
        except:
            time.sleep(perTime)
            timeout += perTime
            continue
        else:
            break
    if(moreEle.get_attribute('style') != 'display: none;'):
        timeout = 0
        while True:
            try:
                if timeout >= timeOutTotal:
                    return None
                driver.execute_script('arguments[0].click()', moreEle)
            except Exception as e:
                print(e, 'click more error, again')
                time.sleep(perTime)
                timeout += perTime
                continue
            else:
                break
    for css in hyInfoCSS:
        if isElementPresent(driver, By.CSS_SELECTOR, hyInfoCSS[css]):
            eles = driver.find_elements(by = By.CSS_SELECTOR, value = hyInfoCSS[css])
            infoStr = ''
            for ele in eles:
                infoStr += ele.text
                infoStr += '  '
            save[css] = infoStr
    if isElementPresent(driver, By.CSS_SELECTOR, hy_info):
        eles = driver.find_elements(by = By.CSS_SELECTOR, value = hy_info)
        for ele in eles:
            if(ele.text == '会议名称：'):
                infoStr = ele.find_element(by = By.XPATH, value = '../p').text
                save['hy_hyname'] = infoStr
            elif(ele.text == '会议时间：'):
                infoStr = ele.find_element(by = By.XPATH, value = '../p').text
                save['hy_hytime'] = infoStr
            elif(ele.text == '会议地点：'):
                infoStr = ele.find_element(by = By.XPATH, value = '../p').text
                save['hy_hyplace'] = infoStr
    return save

class crawler(threading.Thread):
    def __init__(self, carrier, index):
        threading.Thread.__init__(self)
        self.pageId = None
        self.carrier = carrier
        self.index = index
        self.driver = None
        self.wxfl = None
        self.ecs = []
        self.necs = []
        self.necTexts = []
        self.count = 0
    def init(self):
        LOGI('init')
    def run(self):
        # try:
        sem.acquire()
        self.driver = openWxfl(self.carrier)
        if not self.driver:
            LOGE('openWxfl error! {}.{}'.format(self.carrier, self.index))
            return
        self.pageId = self.driver.current_window_handle
        flag = True
        while flag:
            try:
                wxflContent = self.driver.find_element(by = By.CSS_SELECTOR, value = 'ul#defult.nav-content-list')
                list = wxflContent.find_elements(by = By.CSS_SELECTOR, value = 'li')
                li = list[self.index]
                self.ecs.append(li)
                self.wxfl = self.ecs[0].text
            except:
                continue
            else:
                flag = False
        self.setName(self.wxfl)
        LOGI('载体:', self.carrier, '\t', '文献分类:', self.wxfl)
        # 获取所有不可扩展分类
        while len(self.ecs):
            li = self.ecs.pop()
            div = li.find_element(by = By.CSS_SELECTOR, value = 'div.item-nav')
            if isElementPresent(div, By.CSS_SELECTOR, 'i.icon'):
                tmpEle = div.find_element(by = By.CSS_SELECTOR, value = 'i.icon')
                self.driver.execute_script('arguments[0].click()', tmpEle)
                WebDriverWait(li, timeOutTotal, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul > li')))
                tmpList = li.find_elements(by = By.CSS_SELECTOR, value = 'ul > li')
                LOGI(div.find_element(by = By.CSS_SELECTOR, value = 'a').text)
                LOGI(len(tmpList))
                for tmpLi in tmpList:
                    self.ecs.append(tmpLi)
            else:
                self.necs.append(div.find_element(by = By.CSS_SELECTOR, value = 'i.icon-select'))
                self.necTexts.append(div.find_element(by = By.CSS_SELECTOR, value = 'a').text)
        for i in range(len(self.necs)):
            # 检索此文献分类
            nec = self.necs[i]
            LOGI(self.necTexts[i])
            str = nec.get_attribute('class')
            strList = str.split(' ')
            if 'selected' not in strList:
                self.driver.execute_script('arguments[0].setAttribute(arguments[1],arguments[2])', nec, 'class', strList[0] + ' selected')
            try:
                WebDriverWait(self.driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.search-btn')))
                self.driver.find_element(by = By.CSS_SELECTOR, value = 'input.search-btn').click()
            except:
                WebDriverWait(self.driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.btn-search')))
                self.driver.find_element(by = By.CSS_SELECTOR, value = 'input.btn-search').click()
            time.sleep(2)
            cnt = processResult(self)
            self.count += cnt
            print('{}: {}'.format(self.necTexts[i], cnt))
            self.driver.execute_script('arguments[0].setAttribute(arguments[1],arguments[2])', nec, 'class', strList[0])
        db = getDB(self.carrier)
        db.summary.update_one(filter = {'class': self.wxfl}, update = {'$set': {'count': self.count}})
        LOGI(self.wxfl, "deinit")
        self.deinit()
        sem.release()
        # except BaseException as e:
        #     print('0',e)
        #     db = getDB(self.carrier)
        #     db.summary.update_one(filter = {'class': self.wxfl}, update = {'$set': {'count': self.count}})
        #     LOGI(self.wxfl, "deinit")
        #     self.deinit()
        #     sem.release()
    def deinit(self):
        self.ecs.clear()
        self.driver.quit()