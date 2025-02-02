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

    def __init__(self,type):
        
        config = self.get_mongodb_config()
        connection_url = f"mongodb://{config['user']}:{config['pass']}@{config['host']}:{config['port']}/"
        self.type = type
        # connection_url = "mongodb://hamed:h123@localhost:27027/?authMechanism=DEFAULT"
        self.client = MongoClient(connection_url)
        self.db = self.client[config['name']]
        if self.type == "home":
            self.collection = self.db[config['collection_home_all']]
        if self.type == "number":
            self.collection = self.db[config['collection_number_all']]
        if self.type == "car":
            self.collection = self.db[config['collection_car_all']]

        # self.collection.create_index([("url", DESCENDING)], unique=True)

    def get_mongodb_config(self):

        mongodb_config = {

            "host": "localhost",
            "port": 27027,
            "user": "hamed",
            "pass": "h123",
            "name": "divar_db",
            "collection_home_all":  "collection_home_all",
            "collection_car_all": "collection_car_all",
            "collection_number_all" : "collection_number_all"
        }

        return mongodb_config

    def InsertItems(self, items): 
        for item in items:
            try:
                result = self.collection(item)
            except Exception as e:
                pass
            

    def InsertItem(self, item): 
        # try:
        self.collection.insert_one(item)
        # except Exception as e:
        #     print(e)

    def FetchOneItem(self):
        return  self.collection.find_one()




