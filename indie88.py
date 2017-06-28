from bs4 import BeautifulSoup

import requests

baseurl = "http://www.indie88.com/song-history"

r  = requests.get(baseurl)

data = r.text

soup = BeautifulSoup(data, "html.parser")

tracks = soup.find_all("div", {"class": "recently-played-song"})
artists = soup.find_all("div", {"class": "recently-played-artist"})
times = soup.find_all("div", {"class": "recently-played-time"})

result = {
    "recent": [
        {
            "song": tracks[i].text,
            "artist": artists[i].text,
            "time": times[i].text
        }
        for i in range(len(tracks))
    ]
}
