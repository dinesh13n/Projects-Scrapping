import pymongo

def getMongoDB (DB_NAME):

    #USER_NAME = 'dinesh' # user name for mongodb
    #PWD = 'es4LYVrr6FUBUNaI' # encripted password for the mongodb
    #PWD = 'mongodb' # encripted password for the mongodb
    #DB_NAME = 'scrapping'
    #COLLECTION_NAME = 'DataHeader'

    # Initialize DataBase connection status to check, if connection established on further process
    dbConStatus = 0

    # Database connection URL
    #CONNECTION_URL = f"mongodb+srv://{USER_NAME}:{PWD}@mongocluster.0tbku.mongodb.net/{DB_NAME}?retryWrites=true&w=majority"
    try:
        client = pymongo.MongoClient("mongodb+srv://dinesh:es4LYVrr6FUBUNaI@mongocluster.0tbku.mongodb.net/scrapping?retryWrites=true&w=majority")
        db = client.test
        dataBase = client[DB_NAME]
        dbConStatus = 1
    except:
        dbConStatus = 0
        pass

    return dbConStatus, dataBase

def getDBCollection(dataBase,collName):

    ## Initialize collection connection status to check, if connection established on further process
    colConStatus = 0

    try :
        collection = dataBase[collName]
        colConStatus = 1
    except:
        colConStatus = 0
        pass

    return colConStatus, collection

