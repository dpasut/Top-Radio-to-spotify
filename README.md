**This application is once again under development. LOTS will change over the coming weeks. Sorry for the lack of development in the last few months.**

# Getting your spotify credentials
1. Go to <https://developer.spotify.com/dashboard/applications> and create your application.
2. Visit the dashboard of your application and get the client id, this is your `spotify_id` and client secret, this is your `spotify_secret`. Your `spotify_username` is the username used to create the application on the Spotify website. 

# Setup
1. Copy `creds.json.example` to `creds.json`, and fill in your `spotify_id`, `spotify_secret`, and `spotify_username`.
2. Run `get-spotify-token.py <your-spotify-username>` and follow the instructions to get a token for accessing your playlist stuff. Put this in your `creds.json` file.

# Usage
1. Run `python2 playlist.py` to scrape the music stream and create/update the playlist! See **Info** for more details.
2. Enjoy!

# Info
All the songs will be stored in `data.db`, and you can look at them using `sqlite3`. To ensure a working version of `sqlite3`, a Docker image has been included. Once Docker is installed, run `make sqlite3`.

Right now, `playlist.py` creates or updates three playlists on your spotify account with the top 100 most played songs in the last week, all time, and of 2017. It uploads the songs in order of play count.

# Automation
A simple bash script, `auto.sh.example` is included to easily keep the playlists up to date with cron. To use:
1. Copy `auto.sh.example` to `auto.sh`
2. Type `chmod +x auto.sh` in terminal.
3. Within `auto.sh`, change `<folder path>` to the correct path.
1. Type `crontab -e` in your terminal
2. Add `0 * * * * /bin/bash <folder path>/auto.sh` to the bottom of the file, changing `<folder path>` to the correct path. This will run *every* 30 minutes.
