from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os

from config.config import settings
from config.database import Database
from api.api_v1.router import router


app = FastAPI(
     title=settings.APP_NAME, 
     version=settings.API_VERSION
)

origins = [
     'http://localhost:5173'
]

app.add_middleware(
     CORSMiddleware,
     allow_origins = origins, 
     allow_credentials = True, 
     allow_methods = ["*"],
     allow_headers = ["*"],
     max_age=3600  # Cache preflight requests for 1 hour
)

# register routes
app.include_router(router, prefix=settings.API_VERSION_STR)

@app.on_event("startup")
async def app_init():
     """
          initialise crucial application services
     """
     try:
          database = Database()
          app.db = database.connect()
          app.db_client = database.get_client()
          print("You successfully connected to MongoDB!")
     except ConnectionError as e:
          print(str(e))


@app.on_event("shutdown")
async def shutdown_db_client():
     app.db_client.close()


@app.get("/", tags=["Root"])
async def read_root():
     return {
          "message": "welcome to cvision API v1"
     }