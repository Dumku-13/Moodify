// script.js - animations, drawer, score rendering, mood UI

/* -------------------
   Utility
------------------- */
function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/* -------------------
   Drawer (Favorites)
------------------- */
const drawer = document.getElementById('favorites-drawer');
const openFavBtn = document.getElementById('open-favs');
const closeFavBtn = document.getElementById('close-favs');

if (openFavBtn) {
  openFavBtn.addEventListener('click', () => {
    drawer.classList.add('open');
    drawer.setAttribute('aria-hidden', 'false');
  });
}

if (closeFavBtn) {
  closeFavBtn.addEventListener('click', () => {
    drawer.classList.remove('open');
    drawer.setAttribute('aria-hidden', 'true');
  });
}

// ESC closes drawer
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && drawer.classList.contains('open')) {
    drawer.classList.remove('open');
    drawer.setAttribute('aria-hidden', 'true');
  }
});

/* -------------------
   Heart Toggle (visual)
------------------- */
document.addEventListener('click', (e) => {
  const t = e.target;
  if (t.classList && t.classList.contains('save-heart')) {
    t.classList.toggle('filled');
  }
});

/* -------------------
   Card animation using MutationObserver
------------------- */
const resultsEl = document.getElementById('results');

function animateCardsOnce() {
  const cards = [...document.querySelectorAll('.song-card')];
  cards.forEach((c, i) => {
    c.classList.remove('enter');
    c.style.setProperty('--i', i);
    c.offsetHeight; // force reflow
    c.classList.add('enter');
  });
}

if (resultsEl) {
  const mo = new MutationObserver((mutations) => {
    let added = false;
    for (const m of mutations) {
      if (m.addedNodes && m.addedNodes.length) {
        added = true;
        break;
      }
    }
    if (added) setTimeout(animateCardsOnce, 40);
  });
  mo.observe(resultsEl, { childList: true });
}

/* -------------------
   Mood Buttons
------------------- */
const moodButtons = [...document.querySelectorAll('[data-mood]')];
const loadingOverlay = document.getElementById('loading-overlay');

/* -------------------
   sendMood()
------------------- */
async function sendMood(mood) {
  if (!mood) return;

  // highlight active button
  moodButtons.forEach(btn => {
    if (btn.dataset.mood === mood) {
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
    } else {
      btn.classList.remove('active');
      btn.setAttribute('aria-pressed', 'false');
    }
  });

  try {
    if (loadingOverlay) loadingOverlay.classList.add('visible');

    const res = await fetch('/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mood })
    });

    let payload = null;
    try {
      payload = await res.json();
    } catch (err) {
      console.error("Bad JSON:", err);
      resultsEl.innerHTML = `<p class="error">Server response invalid.</p>`;
      return;
    }

    if (!res.ok) {
      console.error("Recommend error:", payload);
      resultsEl.innerHTML = `<p class="error">${escapeHtml(payload.error || "Error fetching tracks")}</p>`;
      return;
    }

    const tracks = payload.tracks || [];
    if (!tracks.length) {
      resultsEl.innerHTML = `<p class="empty">No tracks found for "${escapeHtml(mood)}"</p>`;
      return;
    }

    /* -------------------
       Build Song Cards (with score)
    ------------------- */
    const html = tracks.map((t, i) => {
      const art = escapeHtml(t.album_art || 'https://via.placeholder.com/120');
      const name = escapeHtml(t.name || 'Unknown');
      const artists = escapeHtml(t.artists || '');
      const url = escapeHtml(t.spotify_url || '#');
      const id = escapeHtml(t.id || '');

      const pct = Math.round((t.score || 0) * 100);
      const scoreLabel = `${pct}%`;

      return `
        <div class="song-card" style="--i:${i}; display:flex; align-items:flex-start;">
          <img src="${art}" class="album-art" alt="Album art for ${name}">
          <div class="song-mid">
            <div style="display:flex; gap:12px; align-items:center;">
              <div class="song-title">${name}</div>
              <div class="score-badge">${scoreLabel}</div>
            </div>
            <div class="song-artist">${artists}</div>
            <div class="score-small">Match: ${scoreLabel}</div>

            <div class="song-actions">
              <a class="song-link" target="_blank" rel="noopener" href="${url}">Open in Spotify</a>
              <button class="save-heart" data-track-id="${id}" aria-label="Save ${name}">♡</button>
            </div>
          </div>
        </div>
      `;
    }).join("");

    resultsEl.innerHTML = html;

  } catch (err) {
    console.error("Network/server error:", err);
    resultsEl.innerHTML = `<p class="error">Network or server issue.</p>`;
  } finally {
    if (loadingOverlay) loadingOverlay.classList.remove('visible');
  }
}

/* -------------------
   Wire Mood Buttons
------------------- */
moodButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    sendMood(btn.dataset.mood);
  });

  btn.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      btn.click();
    }
  });
});
