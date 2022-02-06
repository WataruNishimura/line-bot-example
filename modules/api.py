import json
import requests
oauth_url_base = "https://api.line.me/oauth2/v2.1"


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