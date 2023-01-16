import datetime
from collections import Counter

class SpotifyFunctions:
    def get_top_tracks(sp):
        """
        Get the users top 10 tracks of the last month. Returns the top tracks
        with the song name and artist. Also returns the seed_tracks for recommendations.
        """
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
        """
        Returns the top 10 listened to artists as a list of artists and their genre(s). Also returns 
        the artist ids for recommendations.
        """
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
        """
        Uses the genres from top artists to find the top 5 most listened to genres of
        the last month.
        """
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
        """
        Returns the track uris of songs that are recommened based on last month's songs,artists 
        and genres.
        """
        seed_genres= []
        for genre in top_genres:
            seed_genres.append(genre[0])
        
        seed_artists = seed_artists[0:2]
        seed_genres = seed_genres[0:2]
        seed_tracks = seed_tracks[0:1]
        tracks = sp.recommendations(seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks, limit=50)["tracks"]
        recommendations = []
        for track in tracks:
            recommendations.append(track["uri"])
        
        return recommendations
    
    def create_playlist(sp, user_id):
        """
        Create a playlist for the user.
        """
        playlist_name = str(datetime.date.today()) + " Recommendations"
        created_playlist = sp.user_playlist_create(user=user_id, name=playlist_name)
        return created_playlist
    
    def add_songs(sp, user_id, playlist_id, recommendations):
        """
        Add the recommended songs into the created playlist.
        """
        sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist_id, tracks=recommendations)