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

import requests
import sqlite3
from datetime import datetime

    # list playlists
    # create if not exist
    # update playlist(s)
    # https://developer.spotify.com/web-api/replace-playlists-tracks/


USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
BASE_LINK = 'http://www.edge.ca/api/v1/music/broadcastHistory?accountID=36&day=-{}'


def find_track_id(artist_name,track_name,track_ids):
    track_name = track_name.replace('The ', '').strip()
    track_name = re.sub(r'\([^)]*\)', '', track_name)
    r = sp.search("artist:{} track:{}*".format(artist_name, track_name), type='track')

    for track in r['tracks']['items']:
        track_id = track['id']
        track_ids.append(track_id)
        break


if __name__ == '__main__':

    # Load database and create table, if it doesn't exist already
    with sqlite3.connect('data.db') as conn:
        conn.executescript(open('schema.sql').read())
        cur = conn.cursor()
        # TODO: Fix timezone crap
        cur.execute("select coalesce(max(date(date)), '2016-12-29') from raw_data")
        min_date = cur.fetchone()[0]
        min_date = datetime(int(min_date[0:4]),
                            int(min_date[5:7]),
                            int(min_date[8:10]))
        day_range = (datetime.today() - min_date).days
        for i in tqdm(range(day_range + 1)):
            data = requests.get(BASE_LINK.format(i),
                                headers={'User-Agent': USER_AGENT}).json()
            date = data['data']['startDate']
            conn.execute("""
                         INSERT OR REPLACE INTO raw_data (date, data)
                         SELECT datetime(?, 'start of day'), ?
                         """,
                         (date, json.dumps(data)))
            conn.commit()

        # Create a list of song data from last_week_songs table
        cur.execute('select * from last_week_songs order by play_count desc, random()')
        song_data = cur.fetchall()

    # Log into Spotify and get username
    cred = Credentials()
    token = cred.spotify_user_access_token
    username = cred.spotify_username
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    # Get a list of playlist names and ids
    results = sp.current_user_playlists(limit=50)
    names = [a['name'] for a in results['items']]
    playlist_ids = [b['id'] for b in results['items']]


    # Create a new playlist if it does not exist already,
    # Get playlist id if it does exist
    need_new = True

    for name in names:
        if name == "Top 100 on The Edge":
            playlist_id = playlist_ids[names.index(name)]
            need_new = False


    if need_new == True:
        playlists = sp.user_playlist_create(username,"Top 100 on The Edge")
        playlist_id = playlists['id']

    # Find track ids for each song in song_data
    # TODO cache ids for speed improvment
    track_ids = []
    for i in tqdm(range(min(len(song_data),100))):
        find_track_id(str(song_data[i][0]),str(song_data[i][1]),track_ids)


    # Upload songs to Spotify!
    tracks = sp.user_playlist_replace_tracks(username, playlist_id, track_ids)
    print(len(track_ids), 'songs uploaded to spotify! Enjoy!')
