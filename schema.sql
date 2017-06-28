CREATE TABLE IF NOT EXISTS raw_data
(
  station TEXT NOT NULL,
  date TIMESTAMPTZ NOT NULL PRIMARy KEY,
  data JSONB
);

CREATE VIEW IF NOT EXISTS songs_edge
AS
WITH base AS
(
  SELECT json_each.value AS song
  FROM json_each(json(data), '$.data.songs'), raw_data
  WHERE station = 'edge'
)
SELECT 'edge' AS station,
       json_extract(song, '$.artist_name') AS artist,
       json_extract(song, '$.song_name') AS song,
       json_extract(song, '$.last_played') AS play_time
FROM base;

CREATE VIEW IF NOT EXISTS songs_indie
AS
WITH base AS
(
  SELECT json_each.value AS song
  FROM json_each(json(data), '$.events'), raw_data
  WHERE station = 'indie'
)
SELECT 'indie' AS station,
       json_extract(song, '$.artist') AS artist,
       json_extract(song, '$.title') AS song,
       json_extract(song, '$.id') AS play_time
FROM base
WHERE json_extract(song, '$.title') != '';

CREATE VIEW IF NOT EXISTS songs
AS
SELECT * FROM songs_edge
UNION
SELECT * FROM songs_indie;

CREATE TABLE IF NOT EXISTS track_id
(
    song_id text NOT NULL PRIMARY KEY,
    artist text NOT NULL,
    song text NOT NULL
);

CREATE VIEW IF NOT EXISTS last_week_songs
AS
SELECT station, artist, song, count(*) AS play_count
FROM songs
WHERE play_time >= CAST(strftime('%s', datetime('now', '-7 days')) AS INTEGER)
GROUP BY station, artist, song;

CREATE VIEW IF NOT EXISTS top_songs_2017
AS
SELECT station, artist, song, count(*) AS play_count
FROM songs
WHERE play_time >= CAST(strftime('%s', datetime('2017-01-01 00:00:01')) AS INTEGER)
AND play_time <= CAST(strftime('%s', datetime('2018-01-01 00:00:01')) AS INTEGER)
GROUP BY station, artist, song;

CREATE VIEW IF NOT EXISTS top_songs_all_time
AS
SELECT station, artist, song, count(*) AS play_count
FROM songs
GROUP BY station, artist, song;
