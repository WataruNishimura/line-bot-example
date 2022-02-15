import json
from typing import Dict, List, Optional
import requests
from models import MessageObject, UserProfile

oauth_url_base = "https://api.line.me/oauth2/v2.1"
api_url_base = "https://api.line.me/v2"
api__auth_url_base = "https://api.line.me/oauth2/v2.1"

class Singleton(object):
    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

class MessagingApi(Singleton):
    def __init__(self, access_token):
        self.access_token = access_token
    
    def getUserProfile(self, userId):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(api_url_base + f"/bot/profile/{userId}",
                                headers=headers)
        if(response.status_code == 200):
          profile = UserProfile.parse_obj(json.loads(response.content.decode("utf-8")))
          return profile
        else:
          logger.error(response.content)
          return
    
    def replyMessage(self, replyToken: str, messages: List[dict]):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {
          "replyToken": replyToken,
          "messages": messages,
        }
        response = requests.post(api_url_base + "/bot/message/reply", json=payload, headers=headers)
        if(response.status_code == 200):
          return True
        else:
          print(response.content)
          return
          

    def getAccessToken(self):
      return self.access_token

    def setAccessToken(self, access_token):
      self.access_token = access_token

def issueChannelAccessToken(jwt) -> Optional[Dict]:
    """issue channel acces token to request line oauth2 api with JSON Web Token

    Args:
        jwt (str): JSON Web Token for authenication.

    Returns:
        Optional[Dict]: If request successes, return Dict includes "access_token" and "key_id". If error raised, return None.
    """
    payload = {
        "grant_type": "client_credentials",
        "client_assertion_type":
        "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt
    }
    response = requests.post(api__auth_url_base + "/", data=payload)
    if(response.status_code == 200):
      response_dictionary = json.loads(response.content.decode())
      return response_dictionary
    else:
      print(f"{response.status_code}: {response.content}")
      return

def verifyChannelAccessToken(access_token) -> bool:
    """Verify channel access token. 

    Args:
        access_token (str): channel access token.

    Returns:
        bool: If channel access token is valid, return True. If not, return False.
    """
    params = {"access_token": access_token}

    response = requests.get(oauth_url_base + "/verify", params=params)
    if (response.status_code == 200):
        return True
    else:
        return False

def getValidChannelAccessToken(jwt):
    params = {
        "client_assertion_type":
        "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt
    }
    response = requests.get(oauth_url_base + "/tokens/kid", params=params)
    dict = json.loads(response.content.decode())
    if (dict["kids"]):
        return dict["kids"]
    else:
        return []


def setWebhookEndpoint(access_token, endpointUrl):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"endpoint": endpointUrl}

    if (len(endpointUrl) <= 500):
        response = requests.put(api_url_base +
                                "/v2/bot/channel/webhook/endpoint",
                                headers=headers,
                                json=payload)
        print(response.request.body)
        if (response.status_code == 200):
            return True
        else:
            if (mode == "development"):
                print(response.content)
                return
            return
