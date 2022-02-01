import json
from urllib import parse
from modules.jwt import getJWTtoken
from fastapi import FastAPI
import requests
import uvicorn

messaging_api_url = "https://api.line.me/oauth2/v2.1"

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, world"}

if __name__ == "__main__":
  jwt = getJWTtoken(".")
  payload = {
    "grant_type": "client_credentials",
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    "client_assertion": jwt 
  }
  token_response = requests.post(messaging_api_url + "/token" , data=payload)
  print(token_response.text)