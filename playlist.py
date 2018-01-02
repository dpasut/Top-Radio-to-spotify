#!/usr/bin/env python2
import json
import re
import arrow
import requests
import spotipy
import sqlite3
import hashlib
import time
import dateutil.parser
import tenacity

from datetime import datetime
from credentials import Credentials
from bs4 import BeautifulSoup
from tqdm import tqdm


USER_AGENT = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
              'like Gecko) Chrome/55.0.2883.87 Safari/537.36')
BASE_LINK_EDGE = ('https://globalnewselection.s3.amazonaws.com/fm-playlist/'
                  'results/CFNYFM_pl_long.js?callback=plCallback')
BASE_LINK_INDIE = ('http://indie.streamon.fm/eventrange/{}-{}.json')


@tenacity.retry(reraise=True,
                wait=tenacity.wait_exponential(),
                stop=tenacity.stop_after_attempt(5))
def get_indie_data(start, end):
    return requests.get(BASE_LINK_INDIE.format(start, end),
                        headers={'User-Agent': USER_AGENT}).json()


@tenacity.retry(reraise=True,
                wait=tenacity.wait_exponential(),
                stop=tenacity.stop_after_attempt(5))
def get_edge_data(days_back):
    return requests.get(BASE_LINK_EDGE.format(days_back),
                        headers={'User-Agent': USER_AGENT}).json()


def md5sum(artist_name, track_name):
    #
    # Create a unique 6 digit integer to order songs by
    # with the same number of plays
    #

    interval_value = 604800  # One week
    interval = int(time.time() / interval_value)
    md5 = hashlib.md5()
    md5.update("{}{}{}".format(artist_name, track_name, interval))
    digest = md5.hexdigest()
    number = int(digest[:6], 16)
    return number


def find_track_id(song_data, track_ids, track_list):
    #
    # Find and cache track ids
    #
    artist_name = str(song_data[1])

    # Remove "The" from track names, and stuff between brackets.
    # No one likes alternate song titles
    track_name = song_data[2].encode('ascii', 'ignore')
    track_name = str(track_name).replace('The ', '').strip()
    track_name = re.sub(r'\([^)]*\)', '', track_name)

    # Check if track is in track_list table, if it is, use that track_id
    search_new = True
    for track in track_list:
        if (artist_name == str(track[1])) and (track_name == track[2]):
            trackID = track[0]
            track_ids.append(trackID)
            search_new = False
            break

    # If track was NOT found in track_list table, search spotify,
    # get track id, and update the table
    if search_new is True:
        r = sp.search("artist:{} track:{}*".format(artist_name, track_name),
                      type='track')
        for track in r['tracks']['items']:
            trackID = track['id']
            track_ids.append(trackID)
            # update db
            with sqlite3.connect('data.db') as conn:
                conn.execute("""
                             INSERT OR REPLACE INTO track_id
                             VALUES (?, ?, ?)
                             """, (trackID, artist_name, track_name))
                conn.commit()
            break


def load_data():
    # Load database and create table, if it doesn't exist already
    with sqlite3.connect('data.db') as conn:
        conn.executescript(open('schema.sql').read())

        conn.create_function("md5", 2, md5sum)

        cur = conn.cursor()

        # Load 102.1 The Edge songs
        cur.execute('''
                    select coalesce(max(date(date)), '2016-12-29')
                    from raw_data
                    where station = 'edge'
                    ''')
        min_date = cur.fetchone()[0]
        min_date = datetime(int(min_date[0:4]),
                            int(min_date[5:7]),
                            int(min_date[8:10]))
        day_range = (datetime.today() - min_date).days
        for i in tqdm(range(day_range + 1)):
            data = get_edge_data(i)
            date = data['data']['startDate']
            conn.execute("""
                         INSERT OR REPLACE INTO raw_data (station, date, data)
                         SELECT 'edge', datetime(?, 'start of day'), ?
                         """,
                         (date, json.dumps(data)))
            conn.commit()

        # Load Indie 88.1 songs
        cur.execute('''
                    select coalesce(max(date), '2013-08-01 00:00:00')
                    from raw_data
                    where station = 'indie'
                    ''')
        min_date = cur.fetchone()[0]
        min_date = dateutil.parser.parse(min_date)
        day_range = (datetime.today() - min_date).days
        for i in tqdm(range(day_range + 1)):
            start_date = int(time.mktime(min_date.timetuple())
                             + (i * 60 * 60 * 24))
            end_date = int(min(start_date + (60 * 60 * 24), time.time()))
            data = get_indie_data(start_date, end_date)
            date = datetime.strftime(datetime.fromtimestamp(start_date),
                                     '%Y-%m-%d %H:%M:%S')
            if len(data['events']) > 0:
                conn.execute("""
                             INSERT OR REPLACE INTO raw_data
                             (station, date, data)
                             SELECT 'indie', datetime(?, 'start of day'), ?
                             """,
                             (date, json.dumps(data)))
                conn.commit()

        # Get views from database
        cur.execute('''
                    select * from last_week_songs where station = 'edge'
                    order by play_count desc,
                    md5(artist,song)
                    ''')
        song_data_top100 = cur.fetchall()
        cur.execute('''
                    select * from top_songs_2017 where station = 'edge'
                    order by play_count desc,
                    md5(artist,song)
                    ''')
        song_data_2017 = cur.fetchall()
        cur.execute('''
                    select * from top_songs_all_time where station = 'edge'
                    order by play_count desc,
                    md5(artist,song)
                    ''')
        song_data_all_time = cur.fetchall()
        # TODO: Fix md5 for indie songs
        cur.execute('''
                    select * from last_week_songs where station = 'indie'
                    order by play_count desc
                    limit 200
                    ''')
        song_data_top100_indie = cur.fetchall()
        cur.execute('''
                    select * from top_songs_2017 where station = 'indie'
                    order by play_count desc
                    limit 200
                    ''')
        song_data_2017_indie = cur.fetchall()
        cur.execute('''
                    select * from top_songs_all_time where station = 'indie'
                    order by play_count desc
                    limit 200
                    ''')
        song_data_all_time_indie = cur.fetchall()
        # All previously searched songs and ids
        cur.execute('select * from track_id')
        track_list = cur.fetchall()

        return (song_data_top100, song_data_2017, song_data_all_time,
                song_data_top100_indie, song_data_2017_indie,
                song_data_all_time_indie, track_list)


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

    return (sp, username, pl_names, playlist_ids)


def create_update_playlist(playlist_name, song_data, track_id_list,
                           sp, username, pl_names, playlist_ids):
    # Create a new playlist if it does not exist already,
    # Get playlist id if it does exist
    need_new = True
    for name in pl_names:
        if name == playlist_name:
            playlist_id = playlist_ids[pl_names.index(name)]
            need_new = False

    if need_new is True:
        playlists = sp.user_playlist_create(username, playlist_name)
        playlist_id = playlists['id']

    # Find track ids for each song in song_data
    # TODO cache ids for speed improvment
    track_ids = []
    for i in range(len(song_data)):
        if len(track_ids) < 100:
            find_track_id(song_data[i], track_ids, track_id_list)
        else:
            break

    # Upload songs to Spotify!
    sp.user_playlist_replace_tracks(username, playlist_id, track_ids)
    print(len(track_ids),
          "songs uploaded to spotify in playlist", playlist_name)


if __name__ == '__main__':
    (song_data_top100, song_data_2017, song_data_all_time,
     song_data_top100_indie, song_data_2017_indie,
     song_data_all_time_indie, track_id_list) = load_data()
    (sp, username, pl_names, playlist_ids) = log_in()

    playlist_name = "Top 100 This Week on 102.1 The Edge"
    create_update_playlist(playlist_name, song_data_top100, track_id_list,
                           sp, username, pl_names, playlist_ids)

    # playlist_2017 = "Top 100 on 102.1 The Edge in 2017"
    # create_update_playlist(playlist_2017, song_data_2017, track_id_list,
    #                      sp, username, pl_names, playlist_ids)

    playlist_all_time = "Top 100 on 102.1 The Edge of All Time"
    create_update_playlist(playlist_all_time, song_data_all_time,
                           track_id_list, sp, username, pl_names, playlist_ids)

    playlist_name = "Top 100 This Week on Indie 88"
    create_update_playlist(playlist_name, song_data_top100_indie,
                           track_id_list, sp, username, pl_names, playlist_ids)

    playlist_2017 = "Top 100 on Indie 88 in 2017"
    create_update_playlist(playlist_2017, song_data_2017_indie, track_id_list,
                           sp, username, pl_names, playlist_ids)

    playlist_all_time = "Top 100 on Indie 88 of All Time"
    create_update_playlist(playlist_all_time, song_data_all_time_indie,
                           track_id_list, sp, username, pl_names, playlist_ids)
