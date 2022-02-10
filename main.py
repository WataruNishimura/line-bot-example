from asyncio.log import logger
from inspect import signature
import json
import os
from traceback import print_tb
import config 
from modules.jwt import getJWTtoken
from fastapi import FastAPI, Request, Response, Header
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import uvicorn
from modules.api import getValidChannelAccessToken, isValidChannelAccessToken, setWebhookEndpoint
import base64
import hashlib
import hmac
from pydantic import BaseModel
import logging

messaging_api_url = "https://api.line.me/oauth2/v2.1"

mode = os.getenv("MODE") if os.getenv("MODE") else "development"
channel_secret = os.getenv("CLIENT_SECRET")
app = FastAPI()


logger = logging.getLogger("uvicorn")
class WebhookData(BaseModel):
  destination: str
  events: list

@app.on_event("startup")
async def startup():

  access_token = ""

  credential = credentials.Certificate("credentials.json")
  firebase_admin.initialize_app(credential=credential, options={
    "databaseURL": "https://darts-chatbot-example-default-rtdb.asia-southeast1.firebasedatabase.app/"
  })

  jwt = getJWTtoken(".")

  payload = {
    "grant_type": "client_credentials",
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    "client_assertion": jwt 
  }

  kids = getValidChannelAccessToken(jwt=jwt) #有効なトークンのkidが返ってくる
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
    return

@app.get("/")
async def root():
  return {"message": f"Hello, world"}

@app.post("/webhook", status_code=200)
async def webhook(
    request: Request,
    response: Response,
    content_length: int = Header(...),
    x_line_signature: str = Header("x-ling-signature"),
):
  logger.log(level=1, msg=request.headers)
  if(content_length > 1_000_000):
    response.status_code = 400
    return {"result": "Content too long"}
  if(x_line_signature):
    return response

if __name__ == "__main__":

  reload = True if(mode == "development") else False

  uvicorn.run("main:app", host="127.0.0.1", port=8080, log_level="info", reload=True)
