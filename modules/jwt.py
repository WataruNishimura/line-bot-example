from lib2to3.pgen2 import token
import jwt
from jwt.algorithms import RSAAlgorithm
import time
import json
from pathlib import Path
import os

mode = os.getenv("MODE") if os.getenv("MODE") else "development"

token_exp = 60*60*24*7 # 60s 60min 24hour 7days

if(mode == "development") :
  token_exp = 60*60*24*1 # 60s 60min 24hour 1day
elif( mode=="production" ):
  token_exp = 60*60*24*30 # 60s 60min 24hour 30day

def getJWTtoken(directory):
  filepath = Path(directory)
  private_key_file = open(filepath / "private_key.json", mode="rt", encoding="utf-8")
  header_file = open(filepath / "header.json", mode="rt", encoding="utf_8")
  private_key = json.load(private_key_file)
  header = json.load(header_file)

  if(mode == "development"):
    print("token expires_in is " + str(token_exp))

  payload = {
    "iss": os.getenv("CLIENT_ID"),
    "sub": os.getenv("CLIENT_ID"),
    "aud": "https://api.line.me/",
    "exp": int(time.time()) + (60*30),
    "token_exp": token_exp
  }

  key = RSAAlgorithm.from_jwk(private_key)
  JWT = jwt.encode(payload, key, algorithm="RS256", headers=header, json_encoder=None)
  return JWT