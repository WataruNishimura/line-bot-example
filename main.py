from cgi import print_environ
import json
import logging
import os
import re
import config
from database import DataBase
from modules.jwt import getJWTtoken
from fastapi import FastAPI, Request, Response, Header
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import uvicorn
from modules.api import MessagingApi, getValidChannelAccessToken, issueChannelAccessToken, setWebhookEndpoint, verifyChannelAccessToken
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
        if (event.type == "message"):
            if (event.message.type == "text"):
                logger.info(event.message.text)
                profile: UserProfile = messaging_api.getUserProfile(
                    event.source.userId)
                replyMessages = [
                    MessageObject(
                        type="text",
                        text=
                        f"{profile.displayName} さんこんにちは。「{event.message.text} 」についてはお答えできません。"
                    ).dict()
                ]
                messaging_api.replyMessage(replyToken=event.replyToken,
                                           messages=replyMessages)
            elif (event.message.type == "image"):
                logger.info(event.message.contentProvider.type)
                profile: UserProfile = messaging_api.getUserProfile(
                    event.source.userId)
                replyMessages = [
                    MessageObject(
                        type="text",
                        text=f"{profile.displayName} さんその画像いいですね").dict()
                ]
                messaging_api.replyMessage(replyToken=event.replyToken,
                                           messages=replyMessages)
        elif (event.type == "follow"):
            logger.info(messaging_api.getAccessToken())
            profile: UserProfile = messaging_api.getUserProfile(
                event.source.userId)
            logger.info(profile.displayName)
            replyMessages = [
                MessageObject(type="text",
                              text=f"{profile.displayName} さんこんにちは。").dict()
            ]
            messaging_api.replyMessage(replyToken=event.replyToken,
                                       messages=replyMessages)


@app.on_event("startup")
async def startup():
    logger = logging.getLogger("uvicorn")

    jwt = getJWTtoken(".")

    print(f"JWT is {type(jwt)}")

    database = DataBase(
        credentialsFile="credentials.json",
        databaseURL=
        "https://darts-chatbot-example-default-rtdb.asia-southeast1.firebasedatabase.app/"
    )

    messaging_api.setAccessToken(access_token=database.getChannelAccessToken(
        jwt=jwt))


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
