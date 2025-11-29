# mood_map.py  (Mood → Spotify parameters)

MOOD_CONFIG = {
    "happy": {
        "seed_genres": ["pop"],
        "seed_tracks": ["030OCtLMrljNhp8OWHBWW3"],
        "target_valence": 0.9,
        "target_energy": 0.75,
        "target_danceability": 0.8,
        "target_tempo": 110
    },
    "sad": {
        "seed_genres": ["acoustic"],
        "seed_tracks": ["5wANPM4fQCJwkGd4rN57mH"],
        "target_valence": 0.15,
        "target_energy": 0.25,
        "target_danceability": 0.2,
        "target_tempo": 70
    },
    "romance": {
        "seed_genres": ["rnb", "soul"],
        "seed_tracks": ["2eAvDnpXP5W0cVtiI0PUxV"],
        "target_valence": 0.7,
        "target_energy": 0.5,
        "target_danceability": 0.5,
        "target_tempo": 80
    },
    "chill": {
        "seed_genres": ["lofi"],
        "seed_tracks": ["3pE4j1NfiDMAdgA1mBq4tC"],
        "target_valence": 0.4,
        "target_energy": 0.25,
        "target_danceability": 0.35,
        "target_tempo": 85
    },
    "energetic": {
        "seed_genres": ["dance"],
        "seed_tracks": ["0lHAMNU8RGiIObScrsRgmP"],
        "target_valence": 0.8,
        "target_energy": 0.95,
        "target_danceability": 0.9,
        "target_tempo": 130
    },
    "study": {
        "seed_genres": ["lofi", "ambient"],
        "seed_tracks": ["3VWwthiY2ofI0V6Aum3nyA"],
        "target_valence": 0.35,
        "target_energy": 0.2,
        "target_danceability": 0.15,
        "target_tempo": 75
    }
}

DEFAULT_REC_COUNT = 10
