from asyncio.log import logger
from email import message
from inspect import signature
import json
import logging
import os
import re
from tkinter import EventType
from typing import Dict
import config
from modules.jwt import getJWTtoken
from fastapi import FastAPI, Request, Response, Header
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import uvicorn
from modules.api import MessagingApi, getValidChannelAccessToken, isValidChannelAccessToken, setWebhookEndpoint
import base64
import hashlib
import hmac
from pydantic import BaseModel
from models import EventObject, MessageObject, UserProfile

messaging_api_url = "https://api.line.me/oauth2/v2.1"
messaging_api = MessagingApi("")

mode = os.getenv("MODE") if os.getenv("MODE") else "development"
channel_secret = os.getenv("CLIENT_SECRET")
app = FastAPI()
class WebhookData(BaseModel):
    destination: str
    events: list

async def webhook_handler(request: Request, response: Response,
                          x_line_signature, webhook_input: WebhookData):
    body = await request.body()
    body = body.decode("utf-8")
    destination = webhook_input.destination
    events = webhook_input.events
    logger = logging.getLogger("uvicorn")
    if (events == []):
        if (x_line_signature):
            hash = hmac.new(channel_secret.encode("utf-8"),
                            body.encode("utf-8"), hashlib.sha256).digest()
            signature = base64.b64encode(hash)
            if (signature.decode("utf-8") == x_line_signature):
                logger.info("LINE Sinature is valid.")
                return
            else:
                logger.error("Invalid message signature")
                response.status_code = 400
                return
        response.status_code = 403
        logger.error("No x-line-sinature spcified.")
        return

    for event in events:
        event = EventObject.parse_obj(event)
        if(event.type == "message"):
          if(event.message.type == "text"):
            logger.info(event.message.text)
            profile: UserProfile = messaging_api.getUserProfile(event.source.userId)
            replyMessages = [MessageObject(type="text", text=f"{profile.displayName} さんこんにちは。「{event.message.text} 」についてはお答えできません。").dict()]
            messaging_api.replyMessage(replyToken=event.replyToken, messages=replyMessages)
          elif(event.message.type == "image"):
            logger.info(event.message.contentProvider.type)
            profile: UserProfile = messaging_api.getUserProfile(event.source.userId)
            replyMessages = [MessageObject(type="text", text=f"{profile.displayName} さんその画像いいですね").dict()]
            messaging_api.replyMessage(replyToken=event.replyToken, messages=replyMessages)
        elif(event.type == "follow"):
          logger.info(messaging_api.getAccessToken())
          profile: UserProfile = messaging_api.getUserProfile(event.source.userId)
          logger.info(profile.displayName)
          replyMessages = [MessageObject(type="text", text=f"{profile.displayName} さんこんにちは。").dict()]
          messaging_api.replyMessage(replyToken=event.replyToken, messages=replyMessages)



@app.on_event("startup")
async def startup():

    access_token = ""
    logger = logging.getLogger("uvicorn")

    credential = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(
        credential=credential,
        options={
            "databaseURL":
            "https://darts-chatbot-example-default-rtdb.asia-southeast1.firebasedatabase.app/"
        })

    jwt = getJWTtoken(".")

    payload = {
        "grant_type": "client_credentials",
        "client_assertion_type":
        "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt
    }

    kids = getValidChannelAccessToken(jwt=jwt)  #有効なトークンのkidが返ってくる
    if (len(kids) == 0):  #発行済みのトークンがなかった場合
        response = requests.post(messaging_api_url + "/token",
                                 data=payload)  #tokenを取得
        token_dictionary = json.loads(response.content.decode())
        ref = db.reference("line/tokens/" + token_dictionary["key_id"])
        ref.set(token_dictionary["access_token"])
        access_token = token_dictionary["access_token"]
    else:  #発行済みのトークンがあった場合
        for index in range(len(kids)):  #取得したkidからDBを走査
            kid = kids[index]
            ref = db.reference("line/tokens/" + kid)
            kid_token = ref.get()
            if (kid_token != None):
                if (isValidChannelAccessToken(kid_token)):
                    if (mode == "development"):
                        print("Retrieved token is valid")
                    access_token = kid_token
                    break
                else:
                    if (mode == "development"):
                        print("Retrieved token is expired")
                    ref.delete()
                    response = requests.post(messaging_api_url + "/token",
                                             data=payload)
                    token_dictionary = json.loads(response.content.decode())
                    ref = db.reference("line/tokens/" +
                                       token_dictionary["key_id"])
                    ref.set(token_dictionary["access_token"])
                    access_token = token_dictionary["access_token"]
                    break
        if (access_token == ""):  # kid から token 情報を得れなかった場合, tokenを取得
            if (mode == "development"):
                print("valid token exists, but no valid token is in database")
            response = requests.post(messaging_api_url + "/token",
                                     data=payload)
            token_dictionary = json.loads(response.content.decode())
            ref = db.reference("line/tokens/" + token_dictionary["key_id"])
            ref.set(token_dictionary["access_token"])
            access_token = token_dictionary["access_token"]

    messaging_api.setAccessToken(access_token=access_token)


@app.get("/")
async def root():
    return {"message": f"Hello, world"}


@app.post("/webhook", status_code=200)
async def webhook(
        webhook_input: WebhookData,
        request: Request,
        response: Response,
        content_length: int = Header(...),
        x_line_signature: str = Header("x-ling-signature"),
):
    await webhook_handler(request=request,
                          response=response,
                          x_line_signature=x_line_signature,
                          webhook_input=webhook_input)
    return


if __name__ == "__main__":

    reload = True if (mode == "development") else False

    uvicorn.run("main:app",
                host="127.0.0.1",
                port=8080,
                log_level="info",
                reload=True)
