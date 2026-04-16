/**
 * media-gate.js
 * Handles play-count gating for listening and general-topics homework.
 * Works with both <audio> and <video> elements.
 *
 * Usage: include this script on listening.html and general_topics.html
 * Expects global: ASSIGNMENT_ID (int), MEDIA_TYPE ('audio'|'video')
 */

const MediaGate = (() => {
  let playEventId = null;
  let trackingInterval = null;
  let secondsListened = 0;
  let mediaEl = null;
  let gateOpenCallbacks = [];

  function onGateOpen() {
    gateOpenCallbacks.forEach(fn => fn());
  }

  function updateGateUI(status) {
    const playsEl = document.getElementById('playsCompleted');
    const requiredEl = document.getElementById('playsRequired');
    const gateEl = document.getElementById('gateSection');
    const questionsEl = document.getElementById('questionsSection');
    const submitBtn = document.getElementById('submitBtn');
    const playCountBar = document.getElementById('playCountBar');

    if (playsEl) playsEl.textContent = status.plays_completed;
    if (requiredEl) requiredEl.textContent = status.plays_required;

    const pct = Math.min(100, Math.round((status.plays_completed / status.plays_required) * 100));
    if (playCountBar) playCountBar.style.width = pct + '%';

    if (status.gate_open) {
      if (gateEl) gateEl.classList.add('gate-open');
      if (questionsEl) questionsEl.style.display = 'block';
      if (submitBtn) submitBtn.disabled = false;
      onGateOpen();
    }
  }

  async function fetchGateStatus() {
    const res = await fetch(`/api/media/${ASSIGNMENT_ID}/gate-status`);
    if (res.ok) {
      const status = await res.json();
      updateGateUI(status);
      return status;
    }
  }

  async function startPlay() {
    const res = await fetch(`/api/media/${ASSIGNMENT_ID}/play-start?media_type=${MEDIA_TYPE}`, { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      playEventId = data.play_event_id;
      secondsListened = 0;
    }
  }

  async function completePlay() {
    if (!playEventId) return;
    const res = await fetch(`/api/media/${ASSIGNMENT_ID}/play-complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ play_event_id: playEventId, duration_listened: secondsListened }),
    });
    if (res.ok) {
      const status = await res.json();
      updateGateUI(status);
      playEventId = null;
      secondsListened = 0;
    }
  }

  function attach(el) {
    mediaEl = el;

    el.addEventListener('play', () => {
      if (!playEventId) startPlay();
      // Track seconds listened every second
      trackingInterval = setInterval(() => { secondsListened++; }, 1000);
    });

    el.addEventListener('pause', () => {
      clearInterval(trackingInterval);
    });

    el.addEventListener('ended', () => {
      clearInterval(trackingInterval);
      completePlay();
    });

    // Also complete at 90% through (in case user navigates away)
    el.addEventListener('timeupdate', () => {
      if (el.duration && el.currentTime / el.duration >= 0.90 && playEventId) {
        completePlay();
      }
    });
  }

  return {
    init(el) {
      attach(el);
      fetchGateStatus();
    },
    onGateOpen(fn) {
      gateOpenCallbacks.push(fn);
    },
    refresh: fetchGateStatus,
  };
})();
