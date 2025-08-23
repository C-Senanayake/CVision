import uvicorn

from config.config import settings

def main():
     uvicorn.run(
          "app:app", 
          host= settings.HOST,
          reload = settings.DEBUG_MODE,
          port = settings.PORT
     )

if __name__ == "__main__":
     main()