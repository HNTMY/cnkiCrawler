import pymongo

mongoHost = 'localhost'
mongoPort = 27017

def getClient(host = mongoHost, port = mongoPort):
    return pymongo.MongoClient(host, port)

def closeClient(mongoClient):
    mongoClient.close()