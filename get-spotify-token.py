#!/usr/bin/env python2

import spotipy.oauth2 as oauth2
import argparse
from credentials import Credentials

scopes = ['playlist-modify-public', 'playlist-modify-private',
          'playlist-read-private', 'playlist-read-collaborative']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('--force', action='store_true')

    args = parser.parse_args()

    credentials = Credentials()
    sp_oauth = oauth2.SpotifyOAuth(credentials.spotify_id,
                                   credentials.spotify_secret,
                                   "http://localhost/",
                                   scope=' '.join(scopes),
                                   cache_path=".cache-" + args.username)
    token_info = sp_oauth.get_cached_token()

    if not token_info or args.force:
        auth_url = sp_oauth.get_authorize_url()
        print("Please navigate here: {}".format(auth_url))
        print()
        response = raw_input("Enter the URL you were redirected to: ")
        print()
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)

    if token_info:
        print('Your token is:')
        print(token_info['access_token'])
    else:
        print("Can't get token for ", args.username)
