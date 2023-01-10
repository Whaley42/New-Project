import requests
import base64
import datetime
import os


CLIENT_ID = '66682ebcf301458d9c02e709ef13b0db'
CLIENT_CREDS = f"{CLIENT_ID}:{CLIENT_SECRET}"
CLIENT_CREDS_64 = base64.b64encode(CLIENT_CREDS.encode())
TOKEN_URL = "https://accounts.spotify.com/api/token"
TOKEN_DATA = {"grant_type":"client_credentials"}
TOKEN_HEADERS = {
    "Authorization":f"Basic {CLIENT_CREDS_64.decode()}",
    "Content-Type":"application/x-www-form-urlencoded"

}

r = requests.post(TOKEN_URL, data=TOKEN_DATA, headers=TOKEN_HEADERS)

valid_request = r.status_code in range(200, 299)

if valid_request:
    token_response = r.json()

    access_token = token_response['access_token']
    expires_in = token_response['expiries_in']
    
    now = datetime.datetime.now()
    expires = now + datetime.timedelta(seconds=expires_in)
    
    did_expire = expires < now

