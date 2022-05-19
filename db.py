import pymongo
import os

conn_str = os.getenv("MONGO_URL")
db = pymongo.MongoClient(conn_str)
