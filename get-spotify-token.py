#!/usr/bin/env python2

import sys
import json
import spotipy.util as util

scopes = ['playlist-modify-public', 'playlist-modify-private',
          'playlist-read-private', 'playlist-read-collaborative']

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: {} username".format(sys.argv[0]))
    sys.exit()

data = json.load(open('spotify-creds.json'))
token = util.prompt_for_user_token(username, ' '.join(scopes),
                                   data['id'],
                                   data['secret'],
                                   "http://localhost/")

if token:
    print(token)
else:
    print("Can't get token for ", username)
