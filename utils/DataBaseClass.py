# hello_milvus.py demonstrates the basic operations of PyMilvus, a Python SDK of Milvus.
# 1. connect to Milvus
# 2. create collection
# 3. insert data
# 4. create index
# 5. search, query, and hybrid search on entities
# 6. delete entities by PK
# 7. drop collection
import time




import os
from pymongo import MongoClient, DESCENDING

class DBMongo:

    def __init__(self):
        
        # config = self.get_mongodb_config()
        # connection_url = f"mongodb://{config['host']}:{config['port']}"
        connection_url = f"mongodb://localhost:27017"


        self.client = MongoClient(connection_url)
        # self.db = self.client[config['name']]
        # self.collection = self.db[config['collection']]
        self.db = self.client["divar_db"]
        self.collection_all = self.db["all_home_info"]
        self.collection_day = self.db["day_home_info"]


        # self.collection.create_index([("id", DESCENDING)], unique=True)

    def get_mongodb_config(self):

        mongodb_config = {

            "host": os.environ.get("MONGO_HOST"),
            "port": os.environ.get("MONGO_PORT"),
            "user": os.environ.get("MONGO_USERNAME"),
            "pass": os.environ.get("MONGO_PASSWORD"),
            "name": os.environ.get("MONGO_NAME"),
            "collection": os.environ.get("MONGO_COLLECTION")
        }

        return mongodb_config

    def InsertItems(self, items): 

        for item in items:
            try:
                result = self.collection_all.insert_one(item)
            except Exception as e:
                pass

    def InsertItem(self, item): 
        try:
            self.collection_all.insert_one(item)
            self.collection_day.insert_one(item)
        except Exception as e:
            pass

    def FetchOneItem(self):
        return  self.collection.find_one()

    def FetchAllItem(self):
        return  self.collection_day.find({})

    def DropCollection(self):
        self.collection.drop()


