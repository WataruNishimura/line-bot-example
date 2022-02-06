import json
import config
from modules.jwt import getJWTtoken
from fastapi import FastAPI
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
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
  response = requests.post(messaging_api_url + "/token" , data=payload)

  token_dictionary = json.loads(response.content.decode())

  print(token_dictionary["message"])

  credential = credentials.Certificate("credentials.json")
  firebase_admin.initialize_app(credential=credential, options={
    "databaseURL": "https://darts-chatbot-example-default-rtdb.asia-southeast1.firebasedatabase.app/"
  })

  ref = db.reference("line")
  ref.set({
    #"token": token_dictionary.access_token,
    #"key_id": token_dictionary.key_id
  })