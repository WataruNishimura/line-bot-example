import json
from statistics import mode
from aiohttp import request
from grpc import access_token_call_credentials
import requests
oauth_url_base = "https://api.line.me/oauth2/v2.1"
api_url_base = "https://api.line.me/v2"


def isValidChannelAccessToken(access_token):
  params = {
    "access_token": access_token
  }

  response = requests.get(oauth_url_base + "/verify", params= params)
  if(response.status_code == 200) :
    return True
  else:
    return False
  

def getValidChannelAccessToken(jwt):
  params = {
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    "client_assertion": jwt
  }
  response = requests.get(oauth_url_base + "/tokens/kid", params=params)
  dict = json.loads(response.content.decode())
  return dict["kids"]

def setWebhookEndpoint(access_token, endpointUrl):
  headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
  }
  payload = {
    "endpoint": endpointUrl
  }

  if(len(endpointUrl) <= 500):
    response = requests.put(api_url_base + "/v2/bot/channel/webhook/endpoint", headers=headers, json=payload)
    print(response.request.body)
    if(response.status_code == 200) :
      return True
    else: 
      if(mode == "development"):
        print(response.content)
        return
      return