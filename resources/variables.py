import os, spotipy, discord
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFYID"),
    client_secret=os.getenv("SPOTIFYSECRET")
))
version = "2.18.19"
pid = os.getpid()
noMentions = discord.AllowedMentions(roles=False, users=False, replied_user=False)
noRoleMentions = discord.AllowedMentions(roles=False, users=True, replied_user=True)
noReplyMention = discord.AllowedMentions(roles=True, users=True, replied_user=False)
noUserMention = discord.AllowedMentions(roles=True, users=False, replied_user=True)