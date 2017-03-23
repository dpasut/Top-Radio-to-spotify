#!/usr/bin/env python2

import sys
import json
import spotipy.oauth2 as oauth2

scopes = ['playlist-modify-public', 'playlist-modify-private',
          'playlist-read-private', 'playlist-read-collaborative']

if __name__ == '__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Usage: {} username".format(sys.argv[0]))

    data = json.load(open('spotify-creds.json'))
    sp_oauth = oauth2.SpotifyOAuth(data['id'], data['secret'],
                                   "http://localhost/",
                                   scope=' '.join(scopes),
                                   cache_path=".cache-" + username)
    token_info = sp_oauth.get_cached_token()

    if not token_info:
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
        print("Can't get token for ", username)
