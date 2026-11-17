// Shared client code for the practice player, mock builder and question of the day.
import { iconSvg } from '../lib/icons.js';
export const SCORES_KEY = 'fmalt-scores';

export async function loadBank() {
  const r = await fetch('/data/practice.json');
  return r.json();
}

export function loadScores() { try { return JSON.parse(localStorage.getItem(SCORES_KEY) || '{}'); } catch { return {}; } }
export function saveScore(topics, earned, total, id) {
  const s = loadScores();
  for (const t of topics) {
    const row = s[t] || { earned: 0, total: 0, n: 0, ids: [] };
    if (row.ids.includes(id)) continue;
    row.earned += earned; row.total += total; row.n += 1; row.ids.push(id);
    s[t] = row;
  }
  try { localStorage.setItem(SCORES_KEY, JSON.stringify(s)); } catch {}
  return s;
}
export function clearScores() { try { localStorage.removeItem(SCORES_KEY); } catch {} }

export function shuffle(a) { for (let k = a.length - 1; k > 0; k--) { const j = Math.floor(Math.random() * (k + 1)); [a[k], a[j]] = [a[j], a[k]]; } return a; }

export function esc(s) { return String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

/** Build a question card element, with reveals and an optional self-marking row. */
export function card(q, opts = {}) {
  const el = document.createElement('article');
  el.className = 'qcard';
  el.dataset.id = q.id;
  const pill = q.d ? `<span class="pill pill-${q.d.toLowerCase()}">${q.d}</span>` : '';
  const bands = (q.mb || []).map((b) => `<span class="ms-band" style="top:${(b[0] * 100).toFixed(2)}%;height:${((b[1] - b[0]) * 100).toFixed(2)}%"></span>`).join('');
  el.innerHTML = `
    <div class="meta"><strong>${esc(q.s)} · ${q.l === 'AS' ? 'AS ' : ''}${esc(q.p)} · Q${esc(q.q)}</strong><span>${q.m} mark${q.m === 1 ? '' : 's'}</span>${pill}</div>
    ${q.c ? `<img class="crop" src="${q.c}" alt="Question ${esc(q.q)}, ${esc(q.s)} ${esc(q.p)}" decoding="async">` : ''}
    <div class="actions">
      ${q.ms ? `<button class="btn" type="button" data-reveal="ms" aria-expanded="false">${iconSvg('check')}Mark scheme</button>` : ''}
      ${q.e ? `<button class="btn" type="button" data-reveal="er" aria-expanded="false">${iconSvg('comment')}Examiner's comment</button>` : ''}
    </div>
    ${q.ms ? `<div class="reveal" data-panel="ms" hidden><h4>Mark scheme (whole question; this part is marked with the orange bar)</h4><div class="ms-wrap"><img class="crop" data-src="${q.ms}" alt="Mark scheme" decoding="async">${bands}</div>
      ${opts.mark ? `<div class="markrow"><span>Marks you earned:</span>${Array.from({ length: q.m + 1 }, (_, i) => `<button class="chip" type="button" data-mark="${i}">${i}</button>`).join('')}</div>` : ''}</div>` : ''}
    ${q.e ? `<div class="reveal" data-panel="er" hidden><h4>Examiner's comment</h4><p>${esc(q.e)}${q.e.endsWith('…') ? ` <a href="/questions/${q.t[0]}/#${q.id}">Read the full comment</a>` : ''}</p></div>` : ''}`;
  el.querySelectorAll('[data-reveal]').forEach((btn) => btn.addEventListener('click', () => {
    const panel = el.querySelector(`[data-panel="${btn.dataset.reveal}"]`);
    const img = panel.querySelector('img[data-src]');
    if (img) { img.src = img.dataset.src; img.removeAttribute('data-src'); }
    const open = panel.hasAttribute('hidden');
    panel.toggleAttribute('hidden', !open);
    btn.setAttribute('aria-expanded', String(open));
  }));
  el.querySelectorAll('[data-mark]').forEach((b) => b.addEventListener('click', () => {
    el.querySelectorAll('[data-mark]').forEach((x) => x.setAttribute('aria-pressed', 'false'));
    b.setAttribute('aria-pressed', 'true');
    opts.onMark && opts.onMark(Number(b.dataset.mark));
  }));
  return el;
}

export function fmtTime(s) { const m = Math.floor(s / 60), r = s % 60; return `${m}:${String(r).padStart(2, '0')}`; }
