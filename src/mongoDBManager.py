import pymongo

mongoHost = 'localhost'
mongoPort = 27017

def getDB(dbname):
    client = pymongo.MongoClient('localhost', 27017)    # 连接服务器，需要先开启服务
    return client[dbname]

def getCollection(dbname, colName):
    client = pymongo.MongoClient('localhost', 27017)    # 连接服务器，需要先开启服务
    return client[dbname][colName]