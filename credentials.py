import json
import spotipy.oauth2 as oauth2

scopes = ['playlist-modify-public', 'playlist-modify-private',
          'playlist-read-private', 'playlist-read-collaborative']


class Credentials:
    def __init__(self, fn='creds.json'):
        try:
            data = json.load(open(fn))
        except:
            raise Exception('Unable to load credentials from `{}`.'
                            'Copy the example and fill in the values.'
                            .format(fn))
        self.spotify_id = data['spotify_id']
        self.spotify_secret = data['spotify_secret']
        self.spotify_user_access_token = data['spotify_user_access_token']
        self.spotify_username = data['spotify_username']
        if self.spotify_username != '':
            sp_oauth = oauth2.SpotifyOAuth(
                self.spotify_id,
                self.spotify_secret,
                "http://localhost/",
                scope=' '.join(scopes),
                cache_path=".cache-" + self.spotify_username)
            token_info = sp_oauth.get_cached_token()
            if token_info:
                self.spotify_user_access_token = token_info['access_token']
