from pymongo import MongoClient

from config.config import settings

class Database:
     def __init__(self):
          self.db_uri = settings.DB_URI
          self.db_name = settings.DB_NAME
          self.client = None
          self.conn = None
     
     def connect(self):
          try:
               self.client = MongoClient(
                    self.db_uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=60000,
                    socketTimeoutMS=60000,
                    maxPoolSize=10,
                    minPoolSize=1,
                    maxIdleTimeMS=30000 # Close idle connections after 30s
               )
               return self.client[self.db_name]
          except Exception as e:
               raise ConnectionError(f"Error connecting to database: {e}") from e
     
     
     def get_client(self):
          if not self.client:
               raise ConnectionError("Database client is not connected")
          return self.client


