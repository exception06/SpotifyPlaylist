import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint
import os
from dotenv import load_dotenv
import csv

#Scrapping the Billboard 100
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}
URL = "https://www.billboard.com/charts/hot-100/2000-08-12"
response = requests.get(url=URL, headers=header)

soup = BeautifulSoup(response.text, "html.parser")
song_names = soup.select("li ul li h3")
songs = [song.getText().strip() for song in song_names]

scope = "user-library-read playlist-modify-private"

load_dotenv()
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
CLIENT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
                                                client_id=CLIENT_ID,
                                                client_secret=CLIENT_SECRET,
                                                redirect_uri=CLIENT_URI,
                                                show_dialog=True,
                                                cache_path="SpotifyPlaylist/token.txt",
                                                ))

# To get the info related to the user
user_id = sp.current_user()["id"]
# print(user_id)

# Searching Spotify for songs by title
song_uris = []
year = date.split("-")[0]
playlist_data = [] # Playlist data
for song in songs:
    result = sp.search(q=f"track: {song} year: {year}")
    try:
        item = result["tracks"]["items"][0]
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)

        name = item["name"]
        artist = item["artists"][0]["name"]
        album = item["album"]["name"]
        release = item["album"]["release_date"]
        duration = item["duration_ms"] // 1000
        minutes = duration // 60
        seconds = duration % 60
        link = item["external_urls"]["spotify"]
        playlist_data.append([name, artist, album, release, minutes, seconds, link])
        # print(f"{name} by {artist} ({album}, {release}) – {minutes}:{seconds:02d} → {link}")
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# Playlist in the form of csv
with open("SpotifyPlaylist/playlist.csv",  mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["name", "artist", "album", "release", "minutes", "seconds", "link"])
    writer.writerows(playlist_data)

# Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
pprint.pprint(playlist)

# Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
