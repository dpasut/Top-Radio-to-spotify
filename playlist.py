#!/usr/bin/env python2
import sys
from pprint import pprint

import spotipy
import spotipy.util as util
from credentials import Credentials
import json


DATA = [("Milky Chance", "Cocoon"),
        ("Rag'n'bone Man", "Human"),
        ("Twenty One Pilots", "Heavydirtysoul"),
        ("Japandroids", "Near To The Wild Heart Of Life"),
        ("Mother Mother", "The Drugs"),
        ("Green Day", "Still Breathing"),
        ("Cage The Elephant", "Cold Cold Cold"),
        ("Imagine Dragons", "Believer"),
        ("Bastille", "Blame"),
        ("Kings Of Leon", "Reverend")]

if __name__ == '__main__':
    cred = Credentials()

    # list playlists
    # create if not exist
    # get contents
    # compare to DATA
    # if different, change to match
    # https://developer.spotify.com/web-api/replace-playlists-tracks/

    token = cred.spotify_user_access_token


    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    user = sp.current_user()
    username = user['id']

    results = sp.current_user_playlists(limit=50)

    names = [a['name'] for a in results['items']]

    need_new = True


    for name in names:
        if name == "Top 100 on The Edge":
            #update playlist with new top 100
            print("Playlist already exists, update instead")
            need_new = False


    if need_new == True:
        playlists = sp.user_playlist_create(username,"Top 100 on The Edge")
