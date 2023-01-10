from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from collections import Counter, defaultdict
import os
#Ideas:
#Get Top 10 played songs - API DONE
#Get Top 10 played artists - API DONE
#Get Top 5 Genres - API DONE
#Get Recommendations based on top player songs/artists - API DONE

#Design database
#Users Table: email (PK), display name, access_token
#Artists Lookup Table: song_id, arist_name
#Songs Table: song_id (PK), song_name, artists(FK)
#Top Tracks Table: id(PK) user_email (FK), date, song(FK)


#Top Artists Table: id(PK) user_email (FK), date, artist_name

#Genre Lookup Table: id, genre
#Top Genres Table: id (PK), user_email (FK), date, genres(FK)


app = Flask(__name__)
app.secret_key = "id028dj82q9"
app.config['SESSION_COOKIE_NAME'] = 'Cookie'
TOKEN_INFO = "token_info"
CLIENT_ID = "66682ebcf301458d9c02e709ef13b0db"
CLIENT_SECRET = os.getenv("SPOTIFY_SECRET")

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect("/getTracks")

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info["access_token"])
    top_tracks, seed_tracks = get_top_tracks(sp)
    top_artists, seed_artists = get_top_artists(sp)
    top_genres = get_top_genres(top_artists)
    recommendations = get_recommendations(seed_artists, top_genres, seed_tracks, sp)
    
    return recommendations

    
    

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info["expires_at"] - now < 60
    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("redirectPage", _external=True),
        scope="user-library-read user-read-recently-played user-top-read"
    )

def get_top_tracks(sp):
    top_tracks = []
    artists = []
    seed_tracks = []
    track_items = sp.current_user_top_tracks(time_range='short_term', limit=10)["items"]
    for item in track_items:
        song_name = item["name"]
        seed_tracks.append(item["id"])
        artist_list = item["artists"]
        artists = []
        for artist in artist_list:
            artists.append(artist["name"])
        top_tracks.append((song_name, artists))
    return top_tracks, seed_tracks

def get_top_artists(sp):
    top_artists = []
    artist_ids = []
    artist_items = sp.current_user_top_artists(time_range='short_term', limit=10)["items"]
    for item in artist_items:
        artist = (item["name"], item["genres"])
        id = item["id"]
        top_artists.append(artist)
        artist_ids.append(id)
    return top_artists, artist_ids

def get_top_genres(top_artists):
    genre_count = {}
    for artist in top_artists:
        if len(artist) < 2:
            continue
        genres = artist[1]
        for genre in genres:
            if genre not in genre_count:
                genre_count[genre] = 1
            else:
                genre_count[genre] += 1
    counted_genres = Counter(genre_count)
    top_5_genres = counted_genres.most_common(5)
    return top_5_genres

def get_recommendations(seed_artists, top_genres, seed_tracks, sp):
    seed_genres= []
    for genre in top_genres:
        seed_genres.append(genre[0])
    
    seed_artists = seed_artists[0:2]
    seed_genres = seed_genres[0:2]
    seed_tracks = seed_tracks[0:1]
    tracks = sp.recommendations(seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks, limit=10)["tracks"]
    recommendations = []
    for track in tracks:
        song_name = track["name"]
        artist_list = track["artists"]
        artists = []
        for artist in artist_list:
            artists.append(artist["name"])
        recommendations.append((song_name, artists))
    
    return recommendations
        
    
    
    