import json
import os
import config
from modules.jwt import getJWTtoken
from fastapi import FastAPI
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import uvicorn
from modules.api import getValidChannelAccessToken, isValidChannelAccessToken

messaging_api_url = "https://api.line.me/oauth2/v2.1"

mode = os.getenv("MODE") if os.getenv("MODE") else "development"

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

  kids = getValidChannelAccessToken(jwt=jwt)


  credential = credentials.Certificate("credentials.json")
  firebase_admin.initialize_app(credential=credential, options={
    "databaseURL": "https://darts-chatbot-example-default-rtdb.asia-southeast1.firebasedatabase.app/"
  })

  ref = db.reference("line")

  access_token = ""

  if(len(kids) == 0) : #発行済みのトークンがなかった場合
    response = requests.post(messaging_api_url + "/token" , data=payload) #tokenを取得
    token_dictionary = json.loads(response.content.decode())
    ref = db.reference("line/tokens/" + token_dictionary["key_id"])
    ref.set(token_dictionary["access_token"])
    access_token = token_dictionary["access_token"]
  else: #発行済みのトークンがあった場合
    for index in range(len(kids)): #取得したkidからDBを走査
      kid = kids[index]
      ref = db.reference("line/tokens/" + kid)
      kid_token = ref.get()
      if(kid_token != None):
        if(isValidChannelAccessToken(kid_token)):
          if(mode == "development"):
            print("Retrieved token is valid")
          access_token = kid_token
          break
        else:
          if(mode == "development"):
            print("Retrieved token is expired")
          ref.delete()
          response = requests.post(messaging_api_url + "/token" , data=payload) 
          token_dictionary = json.loads(response.content.decode())
          ref = db.reference("line/tokens/" + token_dictionary["key_id"])
          ref.set(token_dictionary["access_token"])
          access_token = token_dictionary["access_token"]
          break
    if(access_token == ""): # kid から token 情報を得れなかった場合, tokenを取得
      if(mode == "development"):
        print("valid token exists, but no valid token is in database")
      response = requests.post(messaging_api_url + "/token" , data=payload) 
      token_dictionary = json.loads(response.content.decode())
      ref = db.reference("line/tokens/" + token_dictionary["key_id"])
      ref.set(token_dictionary["access_token"])
      access_token = token_dictionary["access_token"]
    
  print("access_token is " + access_token)