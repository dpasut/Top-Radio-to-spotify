#!/usr/bin/env python2
import json
import re
import requests
import spotipy
import sqlite3
import sys

from datetime import datetime
from credentials import Credentials
from pprint import pprint
from tqdm import tqdm


USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
BASE_LINK = 'http://www.edge.ca/api/v1/music/broadcastHistory?accountID=36&day=-{}'


def find_track_id(song_data,track_ids,track_list):
    #
    # Find and cache track ids
    #

    artist_name = str(song_data[0])

    # Remove "The" from track names, and stuff between brackets.
    # No one likes alternate song titles
    track_name = str(song_data[1]).replace('The ', '').strip()
    track_name = re.sub(r'\([^)]*\)', '', track_name)

    # Check if track is in track_list table, if it is, use that track_id
    search_new = True
    for i in range(len(track_list)):
        if (artist_name == str(track_list[i][1])) and (track_name == track_list[i][2]):
            trackID = track_list[i][0]
            track_ids.append(trackID)
            search_new = False
            break

    # If track was NOT found in track_list table, search spotify,
    # get track id, and update the table
    if search_new == True:
        r = sp.search("artist:{} track:{}*".format(artist_name, track_name), type='track')
        for track in r['tracks']['items']:
            trackID = track['id']
            track_ids.append(trackID)
            #update db
            with sqlite3.connect('data.db') as conn:
                conn.execute("""
                             INSERT INTO track_id
                             VALUES (?, ?, ?)
                             """,(trackID,artist_name,track_name))
                conn.commit()
            break

def load_data():
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

        #
        # Create a lists of song data tables/views
        #

        # Top songs from last week:
        # TODO: fix random ordering so each run doesn't change the playlist by ~15 songs,
        # some sort of seed would be good
        cur.execute('select * from last_week_songs order by play_count desc, random()')
        song_data_top100 = cur.fetchall()

        # TODO: add top 100 of 2017 playlist
        #cur.execute('select * from 2017_songs order by play_count desc, random()')
        #song_data_2017 = cur.fetchall()

        # All previously searched songs and ids
        cur.execute('select * from track_id')
        track_list = cur.fetchall()

        return (song_data_top100,track_list)
        # return (song_data_top100,song_data_2017,track_list)

def log_in():
    # Log into Spotify and get username
    cred = Credentials()
    token = cred.spotify_user_access_token
    username = cred.spotify_username
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    # Get a list of playlist names and ids for user
    results = sp.current_user_playlists(limit=50)
    pl_names = [a['name'] for a in results['items']]
    playlist_ids = [b['id'] for b in results['items']]

    return (sp,username,pl_names,playlist_ids)

def create_update_playlist(playlist_name,song_data,track_id_list,sp,username,pl_names,playlist_ids):
    # Create a new playlist if it does not exist already,
    # Get playlist id if it does exist
    need_new = True
    for name in pl_names:
        if name == playlist_name:
            playlist_id = playlist_ids[pl_names.index(name)]
            need_new = False

    if need_new == True:
        playlists = sp.user_playlist_create(username,playlist_name)
        playlist_id = playlists['id']

    # Find track ids for each song in song_data
    # TODO cache ids for speed improvment
    track_ids = []
    for i in range(len(song_data)):
        if len(track_ids)<100:
            new_trackID = find_track_id(song_data[i],track_ids,track_id_list)
        else:
            break
    # Upload songs to Spotify!
    tracks = sp.user_playlist_replace_tracks(username, playlist_id, track_ids)
    print(len(track_ids), "songs uploaded to spotify! Enjoy!")


if __name__ == '__main__':
    (song_data_top100, track_id_list) = load_data()
    (sp,username,pl_names,playlist_ids) = log_in()

    playlist_name = "Top 100 on The Edge"
    create_update_playlist(playlist_name,song_data_top100,track_id_list,sp,username,pl_names,playlist_ids)
