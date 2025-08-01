import os, spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFYID"),
    client_secret=os.getenv("SPOTIFYSECRET")
))