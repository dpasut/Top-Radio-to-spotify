import json


class Credentials:
    def __init__(self, fn='creds.json'):
        try:
            data = json.load(open(fn))
        except:
            raise Exception('Unable to load credentials from `{}`. Copy the example and fill in the values.'
                            .format(fn))
        self.spotify_id = data['spotify_id']
        self.spotify_secret = data['spotify_secret']
        self.spotify_user_access_token = data['spotify_user_access_token']
