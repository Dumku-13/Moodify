# Moodify

A small Flask app that turns a mood into a Spotify playlist. Pick how you feel,
get tracks that fit.

## How it works

- `mood_map.py` maps each mood to Spotify audio-feature targets (energy, valence, tempo, seeds).
- `app.py` exposes a JSON endpoint that queries Spotify through [Spotipy](https://spotipy.readthedocs.io/) using the client-credentials flow and batches the results.
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
