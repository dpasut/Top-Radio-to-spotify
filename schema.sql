CREATE TABLE IF NOT EXISTS raw_data
(
  date TIMESTAMPTZ NOT NULL PRIMARy KEY,
  data JSONB
);

CREATE VIEW IF NOT EXISTS songs
AS
WITH base AS
(
  SELECT json_each.value AS song
  FROM json_each(json(data), '$.data.songs'), raw_data
)
SELECT json_extract(song, '$.artist_name') AS artist,
       json_extract(song, '$.song_name') AS song,
       json_extract(song, '$.last_played') AS play_time
FROM base;
