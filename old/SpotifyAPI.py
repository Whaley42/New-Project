import datetime
import base64
import requests

class SpotifyAPI:
    
    def __init__(self, client_id, client_secret) -> None:
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.access_expires = datetime.datetime.now()
        self.TOKEN_URL = "https://accounts.spotify.com/api/token"
        self.TOKEN_DATA = None
        self.TOKEN_HEADERS = None
        self.ACCESS_TOKEN = None
        self.access_token_expired = True
    
    def get_client_creds(self):
        if self.CLIENT_ID == None or self.CLIENT_SECRET == None:
            raise Exception("Must have valid client credentials")
        
        CLIENT_CREDS = f"{self.CLIENT_ID}:{self.CLIENT_SECRET}"
        CLIENT_CREDS_64 = base64.b64encode(CLIENT_CREDS.encode())
        return CLIENT_CREDS_64
    
    def get_token_header(self):
        CLIENT_CREDS_64 = self.get_client_creds()
        TOKEN_HEADERS = {
            "Authorization":f"Basic {CLIENT_CREDS_64.decode()}",
            "Content-Type":"application/x-www-form-urlencoded"

        }
        return TOKEN_HEADERS
    
    def get_token_data(self):
        r = requests.get("https://accounts.spotify.com/authorize?response_type=code&client_id=66682ebcf301458d9c02e709ef13b0db&scope=user-read-recently-played&redirect_uri=http://localhost:8888/callback")
        
        TOKEN_DATA = {"grant_type":"authorization_code",
                      "code":r,
                      "redirect_uri": "http://localhost:8888/callback"                    
                     
                      }
        return TOKEN_DATA
    
    def authentication(self):
        self.TOKEN_DATA = self.get_token_data()
        self.TOKEN_HEADERS = self.get_token_header()
        r = requests.post(self.TOKEN_URL, auth=(self.CLIENT_ID, self.CLIENT_SECRET), data=self.TOKEN_DATA, headers=self.TOKEN_HEADERS)
        print(r.json())
        valid_request = r.status_code in range(200, 299)
        
        if valid_request:
            token_response = r.json()

            self.ACCESS_TOKEN = token_response['access_token']
            expires_in = token_response['expires_in']
            
            now = datetime.datetime.now()
            self.access_expires = now + datetime.timedelta(seconds=expires_in)
            
            self.access_token_expired = self.access_expires < now
            
            return True
        return False