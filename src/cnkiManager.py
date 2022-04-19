# -*- coding:utf-8 -*-
from typing import final
from commontools import *
import threading
import time
import re
from crawler_log import *
from mongoDBManager import *
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

cnkiUrl = 'https://www.cnki.net/'   # 知网主页url
qkNum = 50                          # 单个文献分类学术期刊最大爬取数量
hyNum = 50                          # 单个文献分类会议最大爬取数量

timeOutTotal = 10                   # 超时等待总时间
perTime = 1                         # 轮询时间

qkDB = 'qk'                   # 学术期刊数据库名
hyDB = 'hy'                   # 会议数据库名

cnPercent = 0.3               # 标题中中文所占比例阈值
titleLenThreshold = 4         # 标题长度最小阈值
abstractLenThreshold = 20     # 摘要长度最小阈值

logFile = r'../log/log'

# 学术期刊
qkInfoCSS = {
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
    timeout = 0
    timeoutFlag = False
    while True:
        try:
            if timeout >= timeOutTotal:
                timeoutFlag = True
                break
            LOGI('get driver')
            driver = getChromeDriver(options)

            LOGI('get url')
            driver.get(cnkiUrl)
            homePage = driver.current_window_handle

            LOGI('clickopenwindow')
            highSearch = clickOpenWindow(driver, driver, homePage, By.ID, 'highSearch')
            LOGI('switch to window {}'.format(homePage))
            driver.switch_to.window(homePage)
            LOGI('close homepage')
            driver.close()
            LOGI('switch to window {}'.format(highSearch))
            driver.switch_to.window(highSearch)
            break
        except:
            driver.quit()
            LOGI('select carrier error, try again')
            time.sleep(perTime)
            timeout += perTime
    if timeoutFlag:
        LOGE('select carrier error, quit')
        return None

    timeout = 0
    timeoutFlag = False
    while True:
        try:
            if timeout >= timeOutTotal:
                timeoutFlag = True
                break
            if carrier == 'qk':
                # 点击学术期刊，中文，SCI来源
                WebDriverWait(driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-id="xsqk"]')))
                LOGI('click xsqk')
                driver.find_element(by = By.CSS_SELECTOR, value = 'li[data-id="xsqk"]').click()
                WebDriverWait(driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.ch')))
                LOGI('click cn')
                driver.find_element(by = By.CSS_SELECTOR, value = 'a.ch').click()
                WebDriverWait(driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[key="SI"]')))
                LOGI('click SCI')
                driver.find_element(by = By.CSS_SELECTOR, value = 'input[key="SI"]').click()
                # 点击文献分类
                LOGI('click wxfl')
                driver.find_element(by = By.CSS_SELECTOR, value = 'a.icon-arrow').click()
                break
            elif carrier == 'hy':
                # 点击会议，语种选择中文
                WebDriverWait(driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-id="hy"]')))
                LOGI('click hy')
                driver.find_element(by = By.CSS_SELECTOR, value = 'li[data-id="hy"]').click()
                WebDriverWait(driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-title="语种"]')))
                LOGI('click language')
                driver.find_element(by = By.CSS_SELECTOR, value = 'div[data-title="语种"]').click()
                LOGI('click chinese')
                driver.find_elements(by = By.CSS_SELECTOR, value = 'div[data-title="语种"]>div>ul>li')[1].click()
                # 点击文献分类
                LOGI('click wxfl')
                driver.find_element(by = By.CSS_SELECTOR, value = 'a.icon-arrow').click()
                break
            else:
                driver.quit()
                return None
        except:
            LOGI('select carrier error, try again')
            driver.refresh()
            time.sleep(perTime)
            timeout += perTime
    if timeoutFlag:
        LOGE('select carrier error, quit')
        return None

    return driver

'''
    创建爬虫线程
'''
def crawlerEnter(carrier, index = None):
    driver = openWxfl(carrier)
    if not driver:
        LOGE('openWxfl error {}'.format('crawlerEnter'))
        return None

    while True:
        try:
            LOGI('find wxfl list')
            wxfl = driver.find_element(by = By.CSS_SELECTOR, value = 'ul#defult.nav-content-list')
            LOGI('get wxfl list')
            list = wxfl.find_elements(by = By.CSS_SELECTOR, value = 'li')
            LOGI('ergodic wxfl list')
            for li in list:
                li.text
            break
        except:
            LOGI('open wxfl list failed, again')
            continue
    wxflNum = len(list)
    LOGI(wxflNum)
    classes = []
    for i in range(wxflNum):
        classes.append(list[i].text)
    LOGI('quit driver')
    driver.quit()

    '''
        多线程爬取文献数据
        共分为wxflNum个线程，每个线程创建一个webdriver实例
    '''
    threads_list = []
    # 创建线程
    if index != None:
        tmp_thread = crawler(carrier, index)
        LOGI('{}.{}'.format(carrier, index))
        threads_list.append(tmp_thread)
    else:
        for i in range(wxflNum):
            tmp_thread = crawler(carrier, i)
            LOGI('{}.{}'.format(carrier, i))
            threads_list.append(tmp_thread)
    return threads_list

def processResult(crawler):
    driver = crawler.driver
    newHighSearch = crawler.pageId
    carrier = crawler.carrier
    cnt = 0
    page = 0
    LOGI('switch to {}'.format(newHighSearch))
    driver.switch_to.window(newHighSearch)
    maxNum = 0
    currentWindowsNum = len(driver.window_handles)
    if(carrier == 'qk'):
        maxNum = qkNum
    elif(carrier == 'hy'):
        maxNum = hyNum
    timeoutNum = 0
    if isElementPresent(driver, By.CSS_SELECTOR, 'table.result-table-list>tbody'):
        while True:
            while len(driver.window_handles) != 1:
                LOGI('switch to {}'.format(driver.window_handles[1]))
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
            LOGI('switch to {}'.format(newHighSearch))
            driver.switch_to.window(newHighSearch)
            flag = False
            try:
                LOGI('find tbody')
                tbody = driver.find_element(by = By.CSS_SELECTOR, value = 'table.result-table-list>tbody')
                LOGI('find articles')
                articles = tbody.find_elements(by = By.XPATH, value = './*')
            except:
                if isElementPresent(driver, By.CSS_SELECTOR, 'table.result-table-list>tbody'):
                    LOGE('has tbody, try again')
                    continue
                else:
                    LOGE('hasnot tbody, exit')
                    break
            saves = []
            title = ''
            for i in range(len(articles)):
                article = articles[i]
                newTab = ''
                try:
                    if timeoutNum > timeOutTotal:
                        timeoutNum = 0
                        break
                    WebDriverWait(article, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'td.name>a')))
                    LOGI('find article')
                    art = article.find_element(by = By.CSS_SELECTOR, value = 'td.name>a')
                    LOGI('click article')
                    art.click()
                except StaleElementReferenceException:
                    LOGI('StaleElementReferenceException, exit')
                    if len(driver.window_handles) != currentWindowsNum:
                        LOGI('new tab')
                        newTab = driver.window_handles[len(driver.window_handles)-1]
                        LOGI('switch to {}'.format(newTab))
                        driver.switch_to.window(newTab)
                        LOGI('close {}'.format(newTab))
                        driver.close()
                        LOGI('switch to {}'.format(newHighSearch))
                        driver.switch_to.window(newHighSearch)
                    if i == 0:
                        flag = True
                    break
                except ElementClickInterceptedException:
                    LOGI('ElementClickInterceptedException, try again')
                    time.sleep(2)
                    if len(driver.window_handles) != currentWindowsNum:
                        LOGI('new tab')
                        newTab = driver.window_handles[len(driver.window_handles)-1]
                        LOGI('switch to {}'.format(newTab))
                        driver.switch_to.window(newTab)
                        LOGI('close {}'.format(newTab))
                        driver.close()
                        LOGI('switch to {}'.format(newHighSearch))
                        driver.switch_to.window(newHighSearch)
                    continue
                except TimeoutException:
                    LOGI('TimeoutException, try again')
                    if len(driver.window_handles) != currentWindowsNum:
                        LOGI('new tab')
                        newTab = driver.window_handles[len(driver.window_handles)-1]
                        LOGI('switch to {}'.format(newTab))
                        driver.switch_to.window(newTab)
                        LOGI('close {}'.format(newTab))
                        driver.close()
                        LOGI('switch to {}'.format(newHighSearch))
                        driver.switch_to.window(newHighSearch)
                    continue
                except Exception:
                    LOGI('Exception, exit')
                    timeoutNum += 1
                    if len(driver.window_handles) != currentWindowsNum:
                        LOGI('new tab')
                        newTab = driver.window_handles[len(driver.window_handles)-1]
                        LOGI('switch to {}'.format(newTab))
                        driver.switch_to.window(newTab)
                        LOGI('close {}'.format(newTab))
                        driver.close()
                        LOGI('switch to {}'.format(newHighSearch))
                        driver.switch_to.window(newHighSearch)
                    if i == 0:
                        flag = True
                    break
                try:
                    title = art.text
                except:
                    LOGI('no article, next')
                    if len(driver.window_handles) != currentWindowsNum:
                        LOGI('new tab')
                        newTab = driver.window_handles[len(driver.window_handles)-1]
                        LOGI('switch to {}'.format(newTab))
                        driver.switch_to.window(newTab)
                        LOGI('close {}'.format(newTab))
                        driver.close()
                        LOGI('switch to {}'.format(newHighSearch))
                        driver.switch_to.window(newHighSearch)
                    continue
                LOGI(crawler.wxfl, page, title)
                LOGD('driver handles size:', len(driver.window_handles))
                if len(driver.window_handles) == currentWindowsNum:
                    LOGI('window count: {}'.format(len(driver.window_handles)))
                    LOGI(driver.window_handles, newHighSearch)
                    continue
                try:
                    LOGI('new tab')
                    newTab = driver.window_handles[len(driver.window_handles)-1]
                    LOGI('switch to {}'.format(newTab))
                    driver.switch_to.window(newTab)
                    if(carrier == 'qk'):
                        save = qkResult(driver)
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
                    if len(driver.window_handles) != currentWindowsNum:
                        LOGI('new tab')
                        newTab = driver.window_handles[len(driver.window_handles)-1]
                        LOGI('switch to {}'.format(newTab))
                        driver.switch_to.window(newTab)
                        LOGI('close {}'.format(newTab))
                        driver.close()
                        LOGI('switch to {}'.format(newHighSearch))
                        driver.switch_to.window(newHighSearch)
                    LOGD('driver handles size:', len(driver.window_handles))
                if cnt >= maxNum:
                    break
            if flag:
                continue
            timeoutNum = 0
            if len(saves) > 0:
                mongoClient = getClient()
                collection = mongoClient[crawler.carrier][crawler.wxfl]
                collection.insert_many(saves)
                closeClient(mongoClient)
            if cnt >= maxNum:
                break
            if(isElementPresent(driver, By.CSS_SELECTOR, 'a#PageNext')):
                try:
                    LOGI('find pagenext')
                    nextPage = driver.find_element(by = By.CSS_SELECTOR, value = 'a#PageNext')
                    LOGI('click pagenext')
                    nextPage.click()
                    page += 1
                except:
                    break
            else:
                break
    return cnt

def qkResult(driver):
    # 学术期刊
    if not isElementPresent(driver, By.CSS_SELECTOR, r'span#ChDivSummary'):
        return None
    abstract = driver.find_element(by = By.CSS_SELECTOR, value = r'span#ChDivSummary').text
    cnNum = 0
    totalNum = len(abstract)
    for char in abstract:
        if char >= '\u4e00' and char <= '\u9fa5':
            cnNum += 1
    if cnNum/totalNum < cnPercent or totalNum < abstractLenThreshold:
        LOGI('not chinese abstract: {}'.format(abstract))
        return None
    save = {}
    timeout = 0
    while True:
        try:
            if timeout >= timeOutTotal:
                return None
            LOGI('find more summary')
            moreEle = driver.find_element(by = By.CSS_SELECTOR, value = 'a#ChDivSummaryMore')
            break
        except:
            LOGI('summary more error, try again')
            time.sleep(perTime)
            timeout += perTime
            continue
    LOGI('get more summary style dispaly')
    if(moreEle.get_attribute('style') != 'display: none;'):
        timeout = 0
        while True:
            try:
                if timeout >= timeOutTotal:
                    return None
                LOGI('click more')
                driver.execute_script('arguments[0].click()', moreEle)
                break
            except Exception as e:
                print(e, 'click more error, again')
                time.sleep(perTime)
                timeout += perTime
                continue
    for css in qkInfoCSS:
        if isElementPresent(driver, By.CSS_SELECTOR, qkInfoCSS[css]):
            LOGI('find {}'.format(css))
            eles = driver.find_elements(by = By.CSS_SELECTOR, value = qkInfoCSS[css])
            if len(eles) > 0:
                infoStr = ''
                if css == 'qk_institution':
                    originInstitutionsList = eles[0].find_element(by = By.XPATH, value = '..').text.strip()
                    print(originInstitutionsList)
                    startIndex = 0
                    mid = 0
                    res = re.match(r'\d+\. ', originInstitutionsList)
                    if res is None:
                        for ele in eles:
                            infoStr += ele.text.strip()
                            infoStr += '  '
                    else:
                        while True:
                            startIndex = mid + res.span()[0]
                            mid = mid + res.span()[1]
                            res = re.search(r'\d+\. ', originInstitutionsList[mid:])
                            if res is not None:
                                infoStr += originInstitutionsList[startIndex:mid + res.span()[0]].strip()
                                infoStr += '  '
                            else:
                                infoStr += originInstitutionsList[startIndex:].strip()
                                infoStr += '  '
                                break
                    print(infoStr.strip())
                else:
                    for ele in eles:
                        infoStr += ele.text.strip()
                        infoStr += '  '
                save[css] = infoStr.strip()
    return save

def hyResult(driver):
    # 会议
    if not isElementPresent(driver, By.CSS_SELECTOR, r'span#ChDivSummary'):
        return None
    abstract = driver.find_element(by = By.CSS_SELECTOR, value = r'span#ChDivSummary').text
    cnNum = 0
    totalNum = len(abstract)
    for char in abstract:
        if char >= '\u4e00' and char <= '\u9fa5':
            cnNum += 1
    if cnNum/totalNum < cnPercent or totalNum < abstractLenThreshold:
        LOGI('not chinese abstract: {}'.format(abstract))
        return None
    save = {}
    timeout = 0
    while True:
        try:
            if timeout >= timeOutTotal:
                return None
            LOGI('find more summary')
            moreEle = driver.find_element(by = By.CSS_SELECTOR, value = 'a#ChDivSummaryMore')
            break
        except:
            LOGI('summary more error, try again')
            time.sleep(perTime)
            timeout += perTime
            continue
    LOGI('get more summary style dispaly')
    if(moreEle.get_attribute('style') != 'display: none;'):
        timeout = 0
        while True:
            try:
                if timeout >= timeOutTotal:
                    return None
                LOGI('click more')
                driver.execute_script('arguments[0].click()', moreEle)
                break
            except Exception as e:
                print(e, 'click more error, again')
                time.sleep(perTime)
                timeout += perTime
                continue
    for css in hyInfoCSS:
        if isElementPresent(driver, By.CSS_SELECTOR, hyInfoCSS[css]):
            LOGI('find {}'.format(css))
            eles = driver.find_elements(by = By.CSS_SELECTOR, value = hyInfoCSS[css])
            if len(eles) > 0:
                infoStr = ''
                if css == 'hy_institution':
                    originInstitutionsList = eles[0].find_element(by = By.XPATH, value = '..').text.strip()
                    print(originInstitutionsList)
                    startIndex = 0
                    mid = 0
                    res = re.match(r'\d+. ', originInstitutionsList)
                    if res is None:
                        for ele in eles:
                            infoStr += ele.text.strip()
                            infoStr += '  '
                    else:
                        while True:
                            startIndex = mid + res.span()[0]
                            mid = mid + res.span()[1]
                            res = re.search(r'\d+. ', originInstitutionsList[mid:])
                            if res is not None:
                                infoStr += originInstitutionsList[startIndex:mid + res.span()[0]].strip()
                                infoStr += '  '
                            else:
                                infoStr += originInstitutionsList[startIndex:].strip()
                                infoStr += '  '
                                break
                    print(infoStr.strip())
                else:
                    for ele in eles:
                        infoStr += ele.text.strip()
                        infoStr += '  '
                save[css] = infoStr.strip()
    if isElementPresent(driver, By.CSS_SELECTOR, hy_info):
        LOGI('find {}'.format(hy_info))
        eles = driver.find_elements(by = By.CSS_SELECTOR, value = hy_info)
        for ele in eles:
            if(ele.text == '会议名称：'):
                LOGI('find hyname')
                infoStr = ele.find_element(by = By.XPATH, value = '../p').text.strip()
                save['hy_hyname'] = infoStr.strip()
            elif(ele.text == '会议时间：'):
                LOGI('find hytime')
                infoStr = ele.find_element(by = By.XPATH, value = '../p').text.strip()
                save['hy_hytime'] = infoStr.strip()
            elif(ele.text == '会议地点：'):
                LOGI('find hyolace')
                infoStr = ele.find_element(by = By.XPATH, value = '../p').text.strip()
                save['hy_hyplace'] = infoStr.strip()
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
        self.startIndex = 0
        
        self.logFilePath = logFile
        if self.carrier == 'qk':
            self.logFilePath += '_0_'
        elif self.carrier == 'hy':
            self.logFilePath += '_1_'
        self.logFilePath += str(self.index)

    def init(self):
        if self.startIndex == 0:
            open(self.logFilePath, 'w+', encoding = 'utf-8').close()
        LOGI(self.carrier, self.index, 'init')
    def run(self):
        # try:
        sem.acquire()
        self.init()
        flag = False
        while not flag:
            flag = self.crawlerArticles()
            LOGI(self.wxfl, "deinit")
            self.deinit()
        mongoClient = getClient()
        db = mongoClient[self.carrier]
        db.summary.update_one(filter = {'class': self.wxfl}, update = {'$set': {'count': self.count}})
        closeClient(mongoClient)
        sem.release()
        # except BaseException as e:
        #     print('0',e)
        #     db = getDB(self.carrier)
        #     db.summary.update_one(filter = {'class': self.wxfl}, update = {'$set': {'count': self.count}})
        #     LOGI(self.wxfl, "deinit")
        #     self.deinit()
        #     sem.release()
    def crawlerArticles(self):
        try:
            self.driver = openWxfl(self.carrier)
            if not self.driver:
                LOGE('openWxfl error! {}.{}, try again'.format(self.carrier, self.index))
                return False
            self.pageId = self.driver.current_window_handle
            LOGI('find wxfl list')
            wxflContent = self.driver.find_element(by = By.CSS_SELECTOR, value = 'ul#defult.nav-content-list')
            LOGI('get wxfl list')
            list = wxflContent.find_elements(by = By.CSS_SELECTOR, value = 'li')
            li = list[self.index]
            self.ecs.append(li)
            LOGI('get wxfl text')
            self.wxfl = self.ecs[0].text
        except:
            return False
        self.setName(self.wxfl)
        LOGI('载体:', self.carrier, '\t', '文献分类:', self.wxfl)
        if self.startIndex == 0:
            mongoClient = getClient()
            db = mongoClient[self.carrier]
            db.summary.delete_one({'id': self.index})
            insertDict = {}
            insertDict['id'] = self.index
            insertDict['class'] = self.wxfl
            insertDict['count'] = 0
            db.summary.insert_one(insertDict)
            db[self.wxfl].drop()
            closeClient(mongoClient)
        else:
            mongoClient = getClient()
            db = mongoClient[self.carrier]
            self.count = db[self.wxfl].count_documents({})
            closeClient(mongoClient)
        f = open(self.logFilePath, 'a+', encoding = 'utf-8')
        f.write(self.wxfl)
        f.close()
        # 获取所有不可扩展分类
        while len(self.ecs):
            li = self.ecs.pop()
            LOGI('find item div')
            div = li.find_element(by = By.CSS_SELECTOR, value = 'div.item-nav')
            if isElementPresent(div, By.CSS_SELECTOR, 'i.icon'):
                timeout = 0
                flag = False
                while True:
                    try:
                        if timeout >= timeOutTotal:
                            flag = True
                            break
                        LOGI('find + icon')
                        tmpEle = div.find_element(by = By.CSS_SELECTOR, value = 'i.icon')
                        LOGI('click + icon')
                        self.driver.execute_script('arguments[0].click()', tmpEle)
                        break
                    except:
                        LOGI('click + error, try again')
                        time.sleep(perTime)
                        timeout += perTime
                        continue
                if flag:
                    return False
                timeout = 0
                flag = False
                while True:
                    try:
                        if timeout >= timeOutTotal:
                            flag = True
                            break
                        WebDriverWait(li, timeOutTotal, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul > li')))
                        LOGI('collect list')
                        tmpList = li.find_elements(by = By.CSS_SELECTOR, value = 'ul > li')
                        break
                    except:
                        LOGI('collect ecs error, try again')
                        time.sleep(perTime)
                        timeout += perTime
                        continue
                if flag:
                    return False
                LOGI(div.find_element(by = By.CSS_SELECTOR, value = 'a').text)
                LOGI(len(tmpList))
                for tmpLi in tmpList:
                    self.ecs.append(tmpLi)
            else:
                try:
                    WebDriverWait(li, timeOutTotal, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'i.icon-select')))
                    LOGI('append necs')
                    iconSelect = div.find_element(by = By.CSS_SELECTOR, value = 'i.icon-select')
                    self.necs.append(iconSelect)
                    WebDriverWait(li, timeOutTotal, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a')))
                    LOGI('append necs text')
                    liAText = div.find_element(by = By.CSS_SELECTOR, value = 'a').text
                    LOGI(liAText)
                    self.necTexts.append(liAText)
                except:
                    LOGI('join icon-select failed, next')
        f = open(self.logFilePath, 'a+', encoding = 'utf-8')
        f.write(' {}{}'.format(len(self.necs), '\n'))
        f.close()
        for i in range(self.startIndex, len(self.necs)):
            # 检索此文献分类
            self.startIndex = i
            nec = self.necs[i]
            LOGI(self.necTexts[i])
            debugSelect = 0
            flag = False
            timeout = 0
            while True:
                try:
                    if debugSelect >= 20:
                        return False
                    if timeout >= timeOutTotal:
                        flag = True
                        return False
                    str = nec.get_attribute('class')
                    strList = str.split(' ')
                    if 'selected' not in strList:
                        LOGI('select wxfl')
                        self.driver.execute_script('arguments[0].setAttribute(arguments[1],arguments[2])', nec, 'class', strList[0] + ' selected')
                    break
                except:
                    LOGI('add selected error, try again')
                    debugSelect += 1
                    time.sleep(perTime)
                    timeout += perTime
                    continue
            if flag:
                continue
            while True:
                try:
                    try:
                        WebDriverWait(self.driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.search-btn')))
                        LOGI('click search-btn')
                        self.driver.find_element(by = By.CSS_SELECTOR, value = 'input.search-btn').click()
                        break
                    except:
                        LOGI('click search-btn error, click btn-search')
                        WebDriverWait(self.driver, timeOutTotal, perTime).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.btn-search')))
                        self.driver.find_element(by = By.CSS_SELECTOR, value = 'input.btn-search').click()
                        break
                except:
                    LOGI('click btn-search error, try again')
                    continue
            time.sleep(2)
            cnt = processResult(self)
            self.count += cnt
            print('{}: {}'.format(self.necTexts[i], cnt))
            timeout = 0
            while True:
                try:
                    if debugSelect >= 10:
                        return False
                    if timeout >= timeOutTotal:
                        break
                    LOGI('cancel select wxfl')
                    self.driver.execute_script('arguments[0].setAttribute(arguments[1],arguments[2])', nec, 'class', strList[0])
                    break
                except:
                    LOGI('cancel selected error, try again')
                    debugSelect += 1
                    time.sleep(perTime)
                    timeout += perTime
                    continue
            f = open(self.logFilePath, 'a+', encoding = 'utf-8')
            f.write('\t{} {} {}\n'.format(i, self.necTexts[i], cnt))
            f.close()
        return True

    def setStart(self, index):
        self.startIndex = index

    def deinit(self):
        self.ecs.clear()
        self.necs.clear()
        self.necTexts.clear()
        if self.driver is not None:
            self.driver.quit()
