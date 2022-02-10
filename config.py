from dotenv import load_dotenv
load_dotenv()

import os
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
MODE = os.getenv("MODE")
HOST = os.getenv("HOST")

if __name__ == "__main__":
  print(CLIENT_ID, CLIENT_SECRET, MODE, HOST)