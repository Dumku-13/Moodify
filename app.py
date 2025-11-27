# app.py
import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# third-party Spotify client
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# load .env (SPOT_CLIENT_ID and SPOT_CLIENT_SECRET expected)
load_dotenv()

SPOT_CLIENT_ID = os.getenv("SPOT_CLIENT_ID")
SPOT_CLIENT_SECRET = os.getenv("SPOT_CLIENT_SECRET")

# basic logging so you see errors in console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("moodify")

# minimal Flask app
app = Flask(__name__, static_folder="static", static_url_path="/static")

# create a global spotify client (or None if creds missing)
_spotify = None
def get_spotify_client():
    global _spotify
    if _spotify:
        return _spotify

    if not SPOT_CLIENT_ID or not SPOT_CLIENT_SECRET:
        logger.error("Missing Spotify credentials in environment.")
        return None

    auth = SpotifyClientCredentials(client_id=SPOT_CLIENT_ID, client_secret=SPOT_CLIENT_SECRET)
    _spotify = spotipy.Spotify(client_credentials_manager=auth, requests_timeout=10, retries=2)
    return _spotify

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    """
    Expects JSON: { "mood": "happy" }
    Returns: { "tracks": [ {id, name, artists, spotify_url, album_art}, ... ] }
    """
    data = request.get_json(silent=True) or {}
    mood = (data.get("mood") or "").strip()
    if not mood:
        return jsonify({"error": "No mood provided"}), 400

    sp = get_spotify_client()
    if sp is None:
        return jsonify({"error": "Spotify credentials not configured on server"}), 500

    try:
        # Search tracks by mood keyword
        # We ask for 20 results then pick up to 10 unique tracks
        resp = sp.search(q=mood, type="track", limit=20, market="US")
        items = resp.get("tracks", {}).get("items", [])
        tracks = []
        seen = set()
        for it in items:
            tid = it.get("id")
            if not tid or tid in seen:
                continue
            seen.add(tid)

            name = it.get("name")
            artists = ", ".join([a.get("name") for a in it.get("artists", []) if a.get("name")])
            spotify_url = it.get("external_urls", {}).get("spotify")
            # album art: try to pick a small image
            album_images = it.get("album", {}).get("images", [])
            album_art = album_images[-1]["url"] if album_images else None

            tracks.append({
                "id": tid,
                "name": name,
                "artists": artists,
                "spotify_url": spotify_url,
                "album_art": album_art
            })
            if len(tracks) >= 10:
                break

        return jsonify({"tracks": tracks}), 200

    except spotipy.exceptions.SpotifyException as e:
        # Spotipy returns useful details — log them
        logger.exception("Spotify API error:")
        return jsonify({"error": "Spotify API error", "detail": str(e)}), 502
    except Exception as e:
        logger.exception("Unexpected error in /search:")
        return jsonify({"error": "Server error", "detail": str(e)}), 500

if __name__ == "__main__":
    # run app
    app.run(debug=True)
