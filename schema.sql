CREATE TABLE IF NOT EXISTS raw_data
(
  date TIMESTAMPTZ NOT NULL PRIMARy KEY,
  data JSONB
);

-- CREATE VIEW songs
-- AS
-- with base as
-- (
--   select jsonb_array_elements(data->'data'->'songs') as song
--   from raw_data
-- )
-- select song->>'artist_name' as artist,
--        song->>'song_name' as song,
--        to_timestamp((song->>'last_played')::bigint) as play_time
-- from base;
