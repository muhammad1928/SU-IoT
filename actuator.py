# import requests, json, hashlib, uuid, time 

# privkey = "ZUXEVEGA9USTAZEWRETHAQUBUR69U6EF"
# # token secret
# secret ="ecd6a7203c64ec98469df1da577eeff3"
# pubkey = "FEHUVEW84RAFR5SP22RABURUPHAFRUNU"
# token="8aba8385b6f65e0f7bf274e5e673f04b05d541a1e"
# # Public key:        FEHUVEW84RAFR5SP22RABURUPHAFRUNU

# # Private key:       ZUXEVEGA9USTAZEWRETHAQUBUR69U6EF

# # Token:               8aba8385b6f65e0f7bf274e5e673f04b05d541a1e

# # Token secret:    ecd6a7203c64ec98469df1da577eeff3
# localtime = time.localtime(time.time()) 
# timestamp = str(time.mktime(localtime)) 
# nonce = uuid.uuid4().hex 
# oauthSignature = (privkey + "%26" + secret) 
# # GET-request 
# def turnOn():
#     response = requests.get(
#         url="https://pa-api.telldus.com/json/device/turnOn", 
#         params={  
#             "id": "11504889",  # only for testing but it does not work
#             # "includeValues": "1", 
#             }, 
#             headers={ 
#                 "Authorization": 'OAuth oauth_consumer_key="{pubkey}", oauth_nonce="{nonce}", oauth_signature="{oauthSignature}", oauth_signature_method="PLAINTEXT", oauth_timestamp="{timestamp}", oauth_token="{token}", oauth_version="1.0"'.format(pubkey=pubkey, nonce=nonce, oauthSignature=oauthSignature, timestamp=timestamp, token=token), }, ) 

# def turnOff():
#     response = requests.get(
#         url="https://pa-api.telldus.com/json/device/turnOff", 
#         params={ 
#             "id": "11504889", # only for testing but it does not work
#             # "includeValues": "1", 
#             }, 
#             headers={ 
#                 "Authorization": 'OAuth oauth_consumer_key="{pubkey}", oauth_nonce="{nonce}", oauth_signature="{oauthSignature}", oauth_signature_method="PLAINTEXT", oauth_timestamp="{timestamp}", oauth_token="{token}", oauth_version="1.0"'.format(pubkey=pubkey, nonce=nonce, oauthSignature=oauthSignature, timestamp=timestamp, token=token), }, ) 
    
#     # # Output/response from GET-request  
#     # responseData = response.json() 
#     # # print(responseData) 
#     # print(json.dumps(responseData, indent=4, sort_keys=True)) 

import requests
import json
import time, hashlib, uuid

privkey = "ZUXEVEGA9USTAZEWRETHAQUBUR69U6EF"
secret ="ecd6a7203c64ec98469df1da577eeff3"
pubkey = "FEHUVEW84RAFR5SP22RABURUPHAFRUNU"
token="8aba8385b6f65e0f7bf274e5e673f04b05d541a1e"
localtime = time.localtime(time.time()) 
timestamp = str(time.mktime(localtime)) 
nonce = uuid.uuid4().hex 
oauthSignature = (privkey + "%26" + secret) 

def turnOn():
    response = requests.get(
        url="https://pa-api.telldus.com/json/device/turnOn",
        params={
            "id": "11504889",  # only for testing but it does not work
        },
        headers={
            "Authorization": 'OAuth oauth_consumer_key="{pubkey}", oauth_nonce="{nonce}", oauth_signature="{oauthSignature}", oauth_signature_method="PLAINTEXT", oauth_timestamp="{timestamp}", oauth_token="{token}", oauth_version="1.0"'.format(pubkey=pubkey, nonce=nonce, oauthSignature=oauthSignature, timestamp=timestamp, token=token),
        },
    )

def turnOff():
    response = requests.get(
        url="https://pa-api.telldus.com/json/device/turnOff",
        params={
            "id": "11504889",  # only for testing but it does not work
        },
        headers={
            "Authorization": 'OAuth oauth_consumer_key="{pubkey}", oauth_nonce="{nonce}", oauth_signature="{oauthSignature}", oauth_signature_method="PLAINTEXT", oauth_timestamp="{timestamp}", oauth_token="{token}", oauth_version="1.0"'.format(pubkey=pubkey, nonce=nonce, oauthSignature=oauthSignature, timestamp=timestamp, token=token),
        },
    )