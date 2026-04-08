import os, spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFYID"),
    client_secret=os.getenv("SPOTIFYSECRET")
))
version = "2.17.0"
pid = os.getpid()