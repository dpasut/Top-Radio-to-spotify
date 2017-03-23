# Setup
1. Copy `creds.json.example` to `creds.json`, and fill in your `spotify_id` and `spotify_secret`. 
2. Run `get-spotify-token.py <your-spotify-username>` and follow the instructions to get a token for accessing your playlist stuff. Put this in your `creds.json` file.

# Info
Right now, `playlist.py` has an example playlist of 10 tracks in `DATA`. Running `playlist.py` *should* create a playlist on Spotify, and add all the songs to it, in order.

If you want to scrape everything, run `load.py`. All the songs will be stored in `data.db`, and you can look at them using `sqlite3`. Make sure you aren't for some reason using Android's `sqlite3`...
