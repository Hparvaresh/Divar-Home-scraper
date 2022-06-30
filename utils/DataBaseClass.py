# hello_milvus.py demonstrates the basic operations of PyMilvus, a Python SDK of Milvus.
# 1. connect to Milvus
# 2. create collection
# 3. insert data
# 4. create index
# 5. search, query, and hybrid search on entities
# 6. delete entities by PK
# 7. drop collection
import time


from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)



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




class MilvusClass():
    def __init__(self):
        self.host = "localhost"
        self.port = "19530"
        self.create_data_set()
    
    def create_data_set (self):
        connections.connect("default", host=self.host, port=self.port)

        fields = [
                FieldSchema(name="deposit", dtype=DataType.INT64),
                FieldSchema(name="rent", dtype=DataType.DOUBLE),
                FieldSchema(name="floor", dtype=DataType.INT64),
                FieldSchema(name="area", dtype=DataType.INT64),
                FieldSchema(name="age", dtype=DataType.INT64),
                FieldSchema(name="rooms", dtype=DataType.INT64),
                FieldSchema(name="time", dtype=DataType.INT64, is_primary=True, auto_id=False),
                FieldSchema(name="city", dtype=DataType.STRING),
                FieldSchema(name="region", dtype=DataType.STRING),
                FieldSchema(name="url", dtype=DataType.STRING)
                ]

        schema = CollectionSchema(fields, "set fields")
        self.milvusDB = Collection("milvusDB", schema)

    def insert_data(self, list):
        self.milvusDB.insert(list)
    def not_used(self):

        ################################################################################
        # 4. create index
        # We are going to create an IVF_FLAT index for hello_milvus collection.
        # create_index() can only be applied to `FloatVector` and `BinaryVector` fields.
        print(fmt.format("Start Creating index IVF_FLAT"))
        index = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128},
        }

        hello_milvus.create_index("embeddings", index)

        ################################################################################
        # 5. search, query, and hybrid search
        # After data were inserted into Milvus and indexed, you can perform:
        # - search based on vector similarity
        # - query based on scalar filtering(boolean, int, etc.)
        # - hybrid search based on vector similarity and scalar filtering.
        #

        # Before conducting a search or a query, you need to load the data in `hello_milvus` into memory.
        print(fmt.format("Start loading"))
        hello_milvus.load()

        # -----------------------------------------------------------------------------
        # search based on vector similarity
        print(fmt.format("Start searching based on vector similarity"))
        vectors_to_search = entities[-1][-2:]
        search_params = {
            "metric_type": "l2",
            "params": {"nprobe": 10},
        }

        start_time = time.time()
        result = hello_milvus.search(vectors_to_search, "embeddings", search_params, limit=3, output_fields=["random"])
        end_time = time.time()

        for hits in result:
            for hit in hits:
                print(f"hit: {hit}, random field: {hit.entity.get('random')}")
        print(search_latency_fmt.format(end_time - start_time))

        # -----------------------------------------------------------------------------
        # query based on scalar filtering(boolean, int, etc.)
        print(fmt.format("Start querying with `random > 0.5`"))

        start_time = time.time()
        result = hello_milvus.query(expr="random > 0.5", output_fields=["random", "embeddings"])
        end_time = time.time()

        print(f"query result:\n-{result[0]}")
        print(search_latency_fmt.format(end_time - start_time))

        # -----------------------------------------------------------------------------
        # hybrid search
        print(fmt.format("Start hybrid searching with `random > 0.5`"))

        start_time = time.time()
        result = hello_milvus.search(vectors_to_search, "embeddings", search_params, limit=3, expr="random > 0.5", output_fields=["random"])
        end_time = time.time()

        for hits in result:
            for hit in hits:
                print(f"hit: {hit}, random field: {hit.entity.get('random')}")
        print(search_latency_fmt.format(end_time - start_time))

        ###############################################################################
        # 6. delete entities by PK
        # You can delete entities by their PK values using boolean expressions.
        ids = insert_result.primary_keys
        expr = f"pk in [{ids[0]}, {ids[1]}]"
        print(fmt.format(f"Start deleting with expr `{expr}`"))

        result = hello_milvus.query(expr=expr, output_fields=["random", "embeddings"])
        print(f"query before delete by expr=`{expr}` -> result: \n-{result[0]}\n-{result[1]}\n")

        hello_milvus.delete(expr)

        result = hello_milvus.query(expr=expr, output_fields=["random", "embeddings"])
        print(f"query after delete by expr=`{expr}` -> result: {result}\n")


        ###############################################################################
        # 7. drop collection
        # Finally, drop the hello_milvus collection
        print(fmt.format("Drop collection `hello_milvus`"))
        utility.drop_collection("hello_milvus")
