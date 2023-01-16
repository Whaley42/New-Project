from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from Airflow.dags.Classes.SpotifyFunctions import SpotifyFunctions as sf
from Airflow.dags.Classes.SqlFunctions import SqlFunctions
from Airflow.dags.Classes.EmailSender import EmailSender


app = Flask(__name__)
app.secret_key = ""
# app.config['SESSION_COOKIE_NAME'] = 'Cookie'
TOKEN_INFO = "token_info"
CLIENT_ID = ""
CLIENT_SECRET = ""


@app.route('/')
def login():
    """
    Connects the user to the spotify auth.
    """
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    """
    Redirect page after the user signs in. Gets the token information.
    """
    sp_oauth = create_spotify_oauth() 
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect("/success")

@app.route('/success')
def getInfo():
    """
    The redirect page after the user logs into spotify. Gets the intial information 
    about the spotify account. Sends an email to the user of the top songs/artists/genres
    as well as create a recommended playlist. 
    """
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        return redirect("/")
    sp = spotipy.Spotify(auth=token_info["access_token"])
    sql = SqlFunctions()
    es = EmailSender()
    
    token = session.get(TOKEN_INFO, None)
    user_info = sp.current_user()
    email = user_info["email"]
    display_name = user_info["display_name"]
    user_id = user_info["id"]
    refresh_token = token["refresh_token"]

    in_db = sql.check_user_exists(email)
    if in_db:
        print("This code gets executed")
        return "Already Signed up"

    print("This code also gets executed")
    sql.insert_user(email, display_name, refresh_token)

    top_tracks, seed_tracks = sf.get_top_tracks(sp)
    top_artists, seed_artists = sf.get_top_artists(sp)
    top_genres = sf.get_top_genres(top_artists)
    recommendations = sf.get_recommendations(seed_artists, top_genres, seed_tracks, sp)
    es.send_email(top_tracks, top_artists, top_genres, email)
    created_playlist = sf.create_playlist(sp, user_id)
    playlist_id = created_playlist["id"]
    sf.add_songs(sp, user_id, playlist_id, recommendations)
    
    session.clear()

    token = session.get(TOKEN_INFO, None)
  
    return "Success"
    
    

def get_token():
    """
    Get the current token if not expired. Otherwise get a refresh token. 
    """
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
    """
    Connects to the spotify OAUTH.
    """
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("redirectPage", _external=True),
        scope="user-library-read user-top-read user-read-email playlist-modify-public",
        cache_handler=cache_handler
    )


if __name__ == "__main__":
    app.run()