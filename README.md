# Setup
1. Copy `creds.json.example` to `creds.json`, and fill in your `spotify_id`, `spotify_secret`, and `spotify_username`.
2. Run `get-spotify-token.py <your-spotify-username>` and follow the instructions to get a token for accessing your playlist stuff. Put this in your `creds.json` file.

# Usage
1. Run `python2 load.py` to scrape the music stream. See **Info** for more details.
2. Run `python2 playlist.py` to create/update the playlist!
3. Enjoy!

# Info
If you want to scrape everything, run `load.py`. All the songs will be stored in `data.db`, and you can look at them using `sqlite3`. To ensure a working version of `sqlite3`, a Docker image has been included. Once Docker is installed, run `make sqlite3`.

Right now, `playlist.py` creates or updates a single playlist on your spotify account with the top 100 most played songs in the last week. It uploads the songs in order of play count.

More playlist options to come.