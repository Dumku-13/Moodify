# Moodify

A small Flask app that turns a mood into a Spotify playlist. Pick how you feel,
get tracks that fit.

## How it works

- `mood_map.py` maps each mood to target values (valence, energy, danceability, tempo) plus seed genres and tracks.
- `app.py` has `/search` (plain track search) and `/recommend`, which searches Spotify through [Spotipy](https://spotipy.readthedocs.io/) (client-credentials flow), then scores candidates against the mood's audio-feature targets.
- `templates/` and `static/` hold the single-page UI.

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate          # source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env            # add your own Spotify app credentials
python app.py
```

Create credentials at <https://developer.spotify.com/dashboard>. `.env` is gitignored; never commit it.

**Stack:** Python · Flask · Spotipy
