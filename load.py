#!/usr/bin/env python2

import json
import requests
import sqlite3
from tqdm import tqdm
from datetime import datetime

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
BASE_LINK = 'http://www.edge.ca/api/v1/music/broadcastHistory?accountID=36&day=-{}'

if __name__ == '__main__':
    with sqlite3.connect('data.db') as conn:
        conn.executescript(open('schema.sql').read())
        cur = conn.cursor()
        # TODO: Fix timezone crap
        cur.execute("select coalesce(max(date(date)), '2016-12-29') from raw_data")
        min_date = cur.fetchone()[0]
        min_date = datetime(int(min_date[0:4]),
                            int(min_date[5:7]),
                            int(min_date[8:10]))
        day_range = (datetime.today() - min_date).days
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
