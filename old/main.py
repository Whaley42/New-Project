from SpotifyAPI import SpotifyAPI
import requests
import datetime
CLIENT_ID = '66682ebcf301458d9c02e709ef13b0db'
client = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)

client.authentication()
# print(client.ACCESS_TOKEN)
# print("BQDqbDUKmBKnuoMrHntdj5J5R7omfUcfJRV2DbTmJ8EmsM9bkCAKA7ZZKS5feUnj9jFP1xVe8fXO3XVrO85aI71x9UEXBI4kX5cV3qWooC2zqFbUK00sJ8mT2J72K_3qUZbPvxbEY6gZlPQBxA7rE")
headers = {
        "Content-Type" : "application/json",
        "Authorization" : f"Bearer {client.ACCESS_TOKEN}"
    }
now = datetime.datetime.now()
yesterday = now - datetime.timedelta(days=1)
yesterday_unix = int(yesterday.timestamp()) * 1000
print(yesterday_unix)
recent_played_url = "https://api.spotify.com/v1/me/player/recently-played?"
recent_played_request = recent_played_url + f"after={yesterday_unix}&limit=20"

    # Download all songs you've listened to "after yesterday", which means in the last 24 hours      
r = requests.get(recent_played_request, headers = headers)
print(r.status_code)
print(r.text)




