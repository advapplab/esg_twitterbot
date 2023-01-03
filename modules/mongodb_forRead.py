import pymongo
import modules.mongodb_static_data as mongodb

class MongoDB:
    
    class DBCollection:
        news_content = 'news_content'
        social_content = 'social_content'
        test = 'test'  # For developer
    
    def __init__(self):
        self.__connection = 'mongodb+srv://{}:{}@{}/'.format(mongodb.StaticData.MGDB_USERNAME, mongodb.StaticData.MGDB_PASSWORD, mongodb.StaticData.MGDB_HOST)
        self.__client = None
        self.__database = None
        self.__collection = None

    # build connect to MongoDB
    def __establish_connection(self, database=mongodb.StaticData.MGDB_DATABASE, collection=None):
        self.__client = pymongo.MongoClient(self.__connection)
        self.__database = self.__client[database]
        self.__collection = self.__database[collection]

    def __close_connection(self):
        self.__client.close()

    # get one data
    def get_content(self, collection, data):
        try:
            self.__establish_connection(collection=collection)
            content = self.__collection.find_one(data)
            return content
        except Exception as e:
            print(e)
        finally:
            self.__close_connection()
    
    def read_prev24hrs_news(self, currTime) :
        try:
            self.__establish_connection(collection='news_content')
            query = { "$and" : [ { "timestamp" : {"$gte" : currTime - 86400 } }, { "timestamp" : {"$lt" : currTime } } ] }
            content = self.__collection.find(query)
            prevDayNews = [ {"content": eachNew["content"], "url": eachNew["url"], "datasource": eachNew["datasource"]} for eachNew in content ]
            return prevDayNews
        except Exception as e:
            print(e)
        finally:
            self.__close_connection()