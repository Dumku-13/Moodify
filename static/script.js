// script.js - animation + drawer + small heart toggle (no persistent storage yet)

// drawer open/close
const drawer = document.getElementById('favorites-drawer');
const openFavBtn = document.getElementById('open-favs');
const closeFavBtn = document.getElementById('close-favs');

if (openFavBtn) openFavBtn.addEventListener('click', () => {
  drawer.classList.add('open');
  drawer.setAttribute('aria-hidden', 'false');
});

if (closeFavBtn) closeFavBtn.addEventListener('click', () => {
  drawer.classList.remove('open');
  drawer.setAttribute('aria-hidden', 'true');
});

// close drawer on ESC
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && drawer.classList.contains('open')) {
    drawer.classList.remove('open');
    drawer.setAttribute('aria-hidden', 'true');
  }
});

// tiny click handler: toggles heart visual state
document.addEventListener('click', (e) => {
  const t = e.target;
  if (t.classList && t.classList.contains('save-heart')) {
    t.classList.toggle('filled');
    // later: add localStorage save here
  }
});

// animate cards when results change (MutationObserver)
const resultsEl = document.getElementById('results');

function animateCardsOnce() {
  const cards = Array.from(document.querySelectorAll('.song-card'));
  cards.forEach((c, i) => {
    // reset if re-rendered
    c.classList.remove('enter');
    // set stagger index
    c.style.setProperty('--i', i);
    // force reflow so animation restarts reliably
    // eslint-disable-next-line no-unused-expressions
    c.offsetHeight;
    c.classList.add('enter');
  });
}

// observe children changes
if (resultsEl) {
  const mo = new MutationObserver((mutations) => {
    // when nodes are added, animate
    let added = false;
    for (const m of mutations) {
      if (m.addedNodes && m.addedNodes.length) { added = true; break; }
    }
    if (added) {
      // small delay so DOM paint finishes
      setTimeout(animateCardsOnce, 40);
    }
  });
  mo.observe(resultsEl, { childList: true, subtree: false });
}
