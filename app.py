# app.py — Moodify (Option C, with batching fix)

import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from mood_map import MOOD_CONFIG, DEFAULT_REC_COUNT

# Load environment
load_dotenv()

SPOT_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOT_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("moodify")


# --------------------------------
# Flask app
# --------------------------------
app = Flask(__name__, static_folder="static", static_url_path="/static")

_spotify = None
def get_spotify_client():
    global _spotify
    if _spotify:
        return _spotify

    if not SPOT_CLIENT_ID or not SPOT_CLIENT_SECRET:
        logger.error("Missing SPOTIPY_CLIENT_ID or SPOTIPY_CLIENT_SECRET in .env")
        return None

    try:
        auth = SpotifyClientCredentials(
            client_id=SPOT_CLIENT_ID,
            client_secret=SPOT_CLIENT_SECRET
        )
        _spotify = spotipy.Spotify(client_credentials_manager=auth, requests_timeout=10, retries=2)
        return _spotify

    except Exception as e:
        logger.exception("Could not create Spotify client")
        return None


# --------------------------------
# Home page
# --------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------
# Legacy /search (still works)
# --------------------------------
@app.route("/search", methods=["POST"])
def search():
    data = request.get_json() or {}
    mood = (data.get("mood") or "").strip()

    if not mood:
        return jsonify({"error": "No mood provided"}), 400

    sp = get_spotify_client()
    if sp is None:
        return jsonify({"error": "Spotify credentials missing"}), 500

    try:
        resp = sp.search(q=mood, type="track", limit=20, market="US")
        items = resp.get("tracks", {}).get("items", [])
        tracks = []
        seen = set()

        for it in items:
            tid = it.get("id")
            if not tid or tid in seen:
                continue
            seen.add(tid)

            artists = ", ".join([a["name"] for a in it.get("artists", [])])
            img = (it.get("album", {}).get("images") or [{}])[-1].get("url", "")

            tracks.append({
                "id": tid,
                "name": it.get("name"),
                "artists": artists,
                "spotify_url": it.get("external_urls", {}).get("spotify", ""),
                "album_art": img
            })

            if len(tracks) >= 10:
                break

        return jsonify({"tracks": tracks}), 200

    except Exception as e:
        logger.exception("Error in /search")
        return jsonify({"error": "Server error", "detail": str(e)}), 500


# --------------------------------
# NEW: /recommend using Option C (audio-features + vibey scoring)
# --------------------------------
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json() or {}
    mood = (data.get("mood") or "").strip()
    count = int(data.get("count", DEFAULT_REC_COUNT))

    if not mood or mood not in MOOD_CONFIG:
        return jsonify({"error": "Invalid or missing mood"}), 400

    cfg = MOOD_CONFIG[mood]
    sp = get_spotify_client()

    if sp is None:
        return jsonify({"error": "Spotify credentials missing"}), 500

    try:
        # 1) Search pool of 30 candidates
        resp = sp.search(q=mood, type="track", limit=30, market="US")
        items = resp.get("tracks", {}).get("items", [])
        if not items:
            return jsonify({"error": "No search results"}), 404

        candidates = []
        ids = []

        for it in items:
            tid = it.get("id")
            if not tid:
                continue

            ids.append(tid)
            img = (it.get("album", {}).get("images") or [{}])[0].get("url", "")

            candidates.append({
                "id": tid,
                "name": it.get("name"),
                "artists": ", ".join([a.get("name", "") for a in it.get("artists", [])]),
                "spotify_url": it.get("external_urls", {}).get("spotify", ""),
                "album_art": img
            })

        # 2) Batch fetch audio features (Spotify rejects very long URLs)
        features_list = []
        BATCH = 10

        for i in range(0, len(ids), BATCH):
            chunk = ids[i:i+BATCH]
            try:
                feats = sp.audio_features(chunk)
                features_list.extend(feats)
            except Exception as e:
                logger.error("Audio-features batch failed: %s", e)
                features_list.extend([None] * len(chunk))

        # 3) Score tracks (vibey, loose)
        weights = {
            "valence": 0.35,
            "energy": 0.30,
            "danceability": 0.20,
            "tempo": 0.15
        }
        MAX_TEMPO = 200.0

        import random
        scored = []

        for cand, feats in zip(candidates, features_list):
            if not feats:
                cand["score"] = 0.0
            else:
                # target mood
                t_val = cfg.get("target_valence", 0.5)
                t_eng = cfg.get("target_energy", 0.5)
                t_dan = cfg.get("target_danceability", 0.5)
                t_tmp = cfg.get("target_tempo", 100)

                # actual
                a_val = float(feats.get("valence") or 0.5)
                a_eng = float(feats.get("energy") or 0.5)
                a_dan = float(feats.get("danceability") or 0.5)
                a_tmp = float(feats.get("tempo") or 100.0)

                # distance
                d_val = abs(a_val - t_val)
                d_eng = abs(a_eng - t_eng)
                d_dan = abs(a_dan - t_dan)
                d_tmp = abs(a_tmp - t_tmp) / MAX_TEMPO

                weighted = (
                    weights["valence"] * d_val +
                    weights["energy"] * d_eng +
                    weights["danceability"] * d_dan +
                    weights["tempo"] * d_tmp
                )

                similarity = max(0.0, 1.0 - weighted)

                # vibey randomness
                jitter = random.uniform(-0.03, 0.06)
                score = max(0, min(1, similarity + jitter))

                cand["score"] = round(score, 4)

            scored.append(cand)

        # 4) Sort + slice
        top = sorted(scored, key=lambda x: x["score"], reverse=True)[:count]

        return jsonify({
            "status": "ok",
            "mood": mood,
            "tracks": top
        }), 200

    except Exception as e:
        logger.exception("Error in /recommend")
        return jsonify({"error": "Server error", "details": str(e)}), 500


# --------------------------------
# Run Dev Server
# --------------------------------
if __name__ == "__main__":
    app.run(debug=True)
