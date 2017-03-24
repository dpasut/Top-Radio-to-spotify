#!/usr/bin/env python2

import json
import requests
import sqlite3
from tqdm import tqdm
from datetime import datetime

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
BASE_LINK = 'http://www.edge.ca/api/v1/music/broadcastHistory?accountID=36&day=-{}'

if __name__ == '__main__':
    day_range = (datetime.today() - datetime(2016, 12, 29)).days
    with sqlite3.connect('data.db') as conn:
        conn.executescript(open('schema.sql').read())
        for i in tqdm(range(day_range + 1)):
            data = requests.get(BASE_LINK.format(i),
                                headers={'User-Agent': USER_AGENT}).json()
            date = data['data']['startDate']
            conn.execute("""
                         INSERT OR REPLACE INTO raw_data (date, data)
                         SELECT datetime(?, 'start of day'), ?
                         """,
                         (date, json.dumps(data)))
            conn.commit()
