#!/usr/bin/env python2
import sys
from pprint import pprint

import spotipy
import spotipy.util as util
from credentials import Credentials
from tqdm import tqdm
import json
import sqlite3
import re



def find_track_id(artist_name,track_name,track_ids):
    track_name = track_name.replace('The ', '').strip()
    track_name = re.sub(r'\([^)]*\)', '', track_name)
    r = sp.search("artist:{} track:{}*".format(artist_name, track_name), type='track')

    for track in r['tracks']['items']:
        track_id = track['id']
        track_ids.append(track_id)
        break

if __name__ == '__main__':
    cred = Credentials()
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('select * from last_week_songs')
    data = c.fetchall()

    # list playlists
    # create if not exist
    # update playlist(s)
    # https://developer.spotify.com/web-api/replace-playlists-tracks/

    token = cred.spotify_user_access_token

    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    user = sp.current_user()
    username = user['id']

    results = sp.current_user_playlists(limit=50)

    names = [a['name'] for a in results['items']]
    playlist_ids = [b['id'] for b in results['items']]

    need_new = True

    track_ids = []

    for name in names:
        if name == "Top 100 on The Edge":
            playlist_id = playlist_ids[names.index(name)]
            need_new = False


    if need_new == True:
        playlists = sp.user_playlist_create(username,"Top 100 on The Edge")
        playlist_id = playlists['id']


    for i in tqdm(range(min(len(data),100))):
        find_track_id(str(data[i][0]),str(data[i][1]),track_ids)

    print(len(track_ids))
    tracks = sp.user_playlist_replace_tracks(username, playlist_id, track_ids)
