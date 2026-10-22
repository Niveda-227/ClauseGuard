/* ClauseGuard web app: talks only to the local server (same origin). No outside requests. */
'use strict';

(() => {
  // One muted ink and one short symbol per category, in the dataset's label order.
  const INK = {
    'Limitation of liability': '#C98A2E',
    'Unilateral termination': '#CF4F65',
    'Unilateral change': '#8B6AE6',
    'Content removal': '#2E97AA',
    'Contract by using': '#3B9467',
    'Choice of law': '#4E72D4',
    'Jurisdiction': '#B08A12',
    'Arbitration': '#B0509F',
  };
  const SYMBOL = {
    'Limitation of liability': 'Li',
    'Unilateral termination': 'Te',
    'Unilateral change': 'Ch',
    'Content removal': 'Rm',
    'Contract by using': 'Us',
    'Choice of law': 'Lw',
    'Jurisdiction': 'Ju',
    'Arbitration': 'Ar',
  };
  const NO_FLAG = 'No category flagged';

  const state = { meta: null, result: null, analyzedText: '', filter: 'all', activeId: null, busy: false };

  const $ = (id) => document.getElementById(id);
  const els = {
    sheet: $('sheet'), terms: $('terms'), doc: $('doc'), count: $('char-count'),
    analyze: $('analyze-btn'), status: $('status'), summary: $('summary'), chips: $('chips'),
    results: $('results'), empty: $('empty'), detail: $('detail'), exports: $('exports'),
    cards: $('cards'), file: $('file-input'), modelLine: $('model-line'),
    specimen: document.querySelector('.specimen'), specimenLines: $('specimen-lines'),
    specimenCaption: $('specimen-caption'),
  };

  // ------------------------------------------------------------------ helpers
  function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
      if (value === null || value === undefined || value === false) continue;
      if (key === 'class') node.className = value;
      else if (key === 'text') node.textContent = value;
      else if (key === 'style') node.style.cssText = value;
      else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
      else node.setAttribute(key, value === true ? '' : value);
    }
    for (const child of children.flat()) {
      if (child !== null && child !== undefined) node.append(child);
    }
    return node;
  }

  function rgba(hex, alpha) {
    const n = parseInt(hex.slice(1), 16);
    return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
  }

  function inkOf(row) {
    return row && row.labels.length ? INK[row.labels[0]] : '#8B6AE6';
  }

  function washFor(labels, alpha) {
    if (!labels.length) return '';
    if (labels.length === 1) {
      const c = rgba(INK[labels[0]], alpha);
      return `linear-gradient(${c}, ${c})`;
    }
    const stops = labels.map((l, i) => `${rgba(INK[l], alpha)} ${Math.round((i / (labels.length - 1)) * 100)}%`);
    return `linear-gradient(90deg, ${stops.join(', ')})`;
  }

  // Same rule as clauses/display.py snippet(): about 60 characters, cut at a word, ending with an ellipsis.
  function snippet(text, width = 60) {
    const clean = text.replace(/\s+/g, ' ').trim();
    if ([...clean].length <= width) return clean;
    let cut = [...clean].slice(0, width - 1).join('');
    const space = cut.lastIndexOf(' ');
    if (space >= Math.floor(width / 2)) cut = cut.slice(0, space);
    return cut.replace(/[ ,;:]+$/, '') + '…';
  }

  function tagEl(label, extra = '') {
    return el('span', { class: `tag ${extra}`.trim(), style: `--ink-c:${INK[label] || '#7A758C'}` },
      el('span', { class: 'dot', 'aria-hidden': 'true' }), el('span', { text: label }));
  }

  function noneTag() {
    return el('span', { class: 'tag tag-none', text: NO_FLAG });
  }

  function rowTags(row) {
    return row.labels.length ? row.labels.map((l) => tagEl(l)) : [noneTag()];
  }

  function setStatus(message, isError = false) {
    els.status.textContent = message;
    els.status.classList.toggle('is-error', isError);
  }

  async function api(path, body) {
    const options = body === undefined ? {} : {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    };
    let response;
    try {
      response = await fetch(path, options);
    } catch (err) {
      throw new Error('The ClauseGuard server is not reachable. Start it with: python -m webapp');
    }
    const type = response.headers.get('Content-Type') || '';
    if (!response.ok) {
      const data = type.includes('json') ? await response.json() : {};
      throw new Error(data.error || `The server answered ${response.status}.`);
    }
    return type.includes('json') ? response.json() : response.blob();
  }

  function download(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = el('a', { href: url, download: filename });
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  // ------------------------------------------------------------------ text input
  function updateCount() {
    const n = [...els.terms.value].length;
    const max = state.meta ? state.meta.max_chars : 100000;
    els.count.textContent = `${n.toLocaleString()} of ${max.toLocaleString()} characters`;
  }

  function setMode(mode) {
    els.sheet.dataset.mode = mode;
    if (mode === 'edit') els.terms.focus({ preventScroll: true });
  }

  function putText(text, message) {
    els.terms.value = text;
    updateCount();
    clearResults(message || 'Text loaded. Choose Analyze terms.');
    setMode('edit');
  }

  function clearResults(message) {
    state.result = null;
    state.analyzedText = '';
    state.activeId = null;
    state.filter = 'all';
    els.doc.textContent = '';
    render();
    if (message) setStatus(message);
  }

  function readFile(file) {
    if (!file) return;
    if (file.size > 1_000_000) {
      setStatus('That file is too large. Use a plain-text file under 1 MB.', true);
      return;
    }
    const reader = new FileReader();
    reader.onload = () => putText(String(reader.result), `Opened ${file.name}. Choose Analyze terms.`);
    reader.onerror = () => setStatus(`Could not read ${file.name}. Save it as UTF-8 text and try again.`, true);
    reader.readAsText(file, 'utf-8');
  }

  // ------------------------------------------------------------------ analysis
  async function runAnalysis() {
    if (state.busy) return;
    const text = els.terms.value;
    if (!text.trim()) {
      setStatus('Paste some text to analyze, or open a .txt file.', true);
      setMode('edit');
      return;
    }
    state.busy = true;
    els.analyze.disabled = true;
    els.analyze.textContent = 'Analyzing…';
    setStatus('Analyzing on this computer…');
    try {
      const { result } = await api('/api/analyze', { text });
      state.result = result;
      state.analyzedText = text;
      state.filter = 'all';
      state.activeId = null;
      renderDoc();
      setMode('read');
      render();
      const flagged = result.sentences.filter((s) => s.labels.length).length;
      setStatus(`${result.sentences.length} sentences, ${flagged} flagged. Model ${result.model_id.slice(0, 12)}. Check the original words.`);
      const first = result.sentences.find((s) => s.labels.length) || result.sentences[0];
      if (first) select(first.sentence_id, { scrollDoc: false });
    } catch (err) {
      setStatus(err.message, true);
    } finally {
      state.busy = false;
      els.analyze.disabled = false;
      els.analyze.textContent = 'Analyze terms';
    }
  }

  function visibleRows() {
    if (!state.result) return [];
    const rows = state.result.sentences;
    if (state.filter === 'all') return rows;
    if (state.filter === 'flagged') return rows.filter((r) => r.labels.length);
    if (state.filter === 'near') return rows.filter((r) => r.near_threshold);
    return rows.filter((r) => r.labels.includes(state.filter));
  }

  // ------------------------------------------------------------------ rendering
  function render() {
    renderSummary();
    renderChips();
    renderResults();
    renderCards();
    const has = Boolean(state.result);
    els.empty.hidden = has;
    els.exports.hidden = !has;
    if (!has) els.detail.hidden = true;
  }

  function renderSummary() {
    if (!state.result) {
      els.summary.textContent = 'No document analysed yet.';
      return;
    }
    const total = state.result.sentences.length;
    const flagged = state.result.sentences.filter((s) => s.labels.length).length;
    els.summary.textContent = `${flagged} of ${total} sentences flagged`;
  }

  function chip(key, label, count, ink) {
    return el('button', {
      class: 'chip', type: 'button', style: ink ? `--ink-c:${ink}` : null,
      'aria-pressed': String(state.filter === key), disabled: count === 0 && state.filter !== key,
      onclick: () => { state.filter = key; renderChips(); renderResults(); },
    }, ink ? el('span', { class: 'dot', 'aria-hidden': 'true' }) : null, `${label} `, el('b', { text: String(count) }));
  }

  function renderChips() {
    els.chips.replaceChildren();
    if (!state.result) return;
    const rows = state.result.sentences;
    const main = el('div', { class: 'chip-row' },
      chip('all', 'All', rows.length),
      chip('flagged', 'Flagged', rows.filter((r) => r.labels.length).length),
      chip('near', 'Near a cut-off', rows.filter((r) => r.near_threshold).length));
    const byCategory = el('div', { class: 'chip-row chip-scroll' });
    for (const label of state.meta.labels) {
      const n = rows.filter((r) => r.labels.includes(label)).length;
      if (n) byCategory.append(chip(label, label, n, INK[label]));
    }
    els.chips.append(main, byCategory);
  }

  function renderResults() {
    els.results.replaceChildren();
    if (!state.result) return;
    const rows = visibleRows();
    if (!rows.length) {
      els.results.append(el('li', { class: 'empty', text: 'No sentences match this filter. Choose All to see every sentence.' }));
      return;
    }
    for (const row of rows) {
      const button = el('button', {
        class: 'result', type: 'button', 'data-id': String(row.sentence_id),
        'aria-current': String(state.activeId === row.sentence_id),
        style: `--active-ink:${inkOf(row)}`,
        onclick: () => select(row.sentence_id, { scrollDoc: true }),
        onkeydown: onResultKey,
      },
      el('span', { class: 'num', text: `${row.sentence_id + 1}.` }),
      el('span', { class: 'tags' }, rowTags(row)),
      el('span', { class: 'snip', text: snippet(row.text) }));
      els.results.append(el('li', {}, button));
    }
  }

  function onResultKey(event) {
    if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
    event.preventDefault();
    const buttons = [...els.results.querySelectorAll('.result')];
    const i = buttons.indexOf(event.currentTarget);
    const next = buttons[i + (event.key === 'ArrowDown' ? 1 : -1)];
    if (next) {
      next.focus();
      select(Number(next.dataset.id), { scrollDoc: true });
    }
  }

  function renderDoc() {
    els.doc.replaceChildren();
    if (!state.result) return;
    // Offsets from the server count characters (code points), so index the text the same way.
    const chars = [...state.analyzedText];
    let cursor = 0;
    for (const row of state.result.sentences) {
      if (row.start > cursor) els.doc.append(chars.slice(cursor, row.start).join(''));
      const classes = ['s'];
      const styles = [`--active-ink:${inkOf(row)}`];
      const title = [row.labels.length ? row.labels.join(', ') : NO_FLAG];
      if (row.labels.length) { classes.push('flagged'); styles.push(`--wash:${washFor(row.labels, 0.17)}`); }
      if (row.near_threshold) classes.push('near');
      els.doc.append(el('span', {
        class: classes.join(' '), 'data-id': String(row.sentence_id), style: styles.join(';'), title: title.join('; '),
        onclick: () => select(row.sentence_id, { scrollDoc: false, fromDoc: true }),
      }, chars.slice(row.start, row.end).join('')));
      cursor = row.end;
    }
    if (cursor < chars.length) els.doc.append(chars.slice(cursor).join(''));
  }

  function select(id, { scrollDoc = true, fromDoc = false } = {}) {
    if (!state.result) return;
    const row = state.result.sentences[id];
    if (!row) return;
    if (fromDoc && !visibleRows().includes(row)) {
      state.filter = 'all';
      renderChips();
      renderResults();
    }
    state.activeId = id;
    for (const b of els.results.querySelectorAll('.result')) {
      b.setAttribute('aria-current', String(Number(b.dataset.id) === id));
    }
    const item = els.results.querySelector(`.result[data-id="${id}"]`);
    if (item) {
      const list = els.results;
      const top = item.offsetTop - list.offsetTop;
      if (top < list.scrollTop || top + item.offsetHeight > list.scrollTop + list.clientHeight) {
        list.scrollTo({ top: Math.max(0, top - list.clientHeight / 3), behavior: 'smooth' });
      }
    }
    if (els.sheet.dataset.mode !== 'read') setMode('read');
    for (const s of els.doc.querySelectorAll('.s.is-active')) s.classList.remove('is-active');
    const span = els.doc.querySelector(`.s[data-id="${id}"]`);
    if (span) {
      span.classList.add('is-active');
      if (scrollDoc) els.doc.scrollTo({ top: Math.max(0, span.offsetTop - els.doc.clientHeight / 3), behavior: 'smooth' });
    }
    renderDetail(row);
  }

  function meter(label, score) {
    const cut = state.meta.thresholds[label];
    return el('div', {},
      el('div', { class: 'meter', style: `--ink-c:${INK[label]}`, role: 'img',
        'aria-label': `Score ${score.toFixed(2)}, cut-off ${cut.toFixed(2)}` },
      el('span', { class: 'fill', style: `width:${Math.max(2, score * 100).toFixed(1)}%` }),
      el('span', { class: 'cut', style: `left:calc(${(cut * 100).toFixed(1)}% - 1px)` })),
      el('div', { class: 'meter-label' },
        el('span', { text: `Score ${score.toFixed(2)}` }),
        el('span', { text: `Cut-off ${cut.toFixed(2)}` })));
  }

  function renderDetail(row) {
    const parts = [
      el('p', { class: 'where', text: `Sentence ${row.sentence_id + 1} of ${state.result.sentences.length}` }),
      el('blockquote', { text: row.text }),
    ];
    for (const label of row.labels) {
      parts.push(el('section', { class: 'reason' },
        el('h4', {}, tagEl(label)),
        el('p', { text: state.meta.explanations[label] }),
        meter(label, row.scores[label])));
    }
    if (!row.labels.length) {
      parts.push(el('p', { class: 'note', text: 'No category flagged. This is not a finding of safety.' }));
    }
    if (row.near_threshold) {
      parts.push(el('p', { class: 'note', text: 'One score is near its decision threshold. Review context carefully.' }));
    }
    els.detail.replaceChildren(...parts);
    els.detail.style.setProperty('--active-ink', inkOf(row));
    els.detail.hidden = false;
  }

  function renderCards() {
    if (!state.meta) return;
    els.cards.replaceChildren();
    for (const label of state.meta.labels) {
      const rows = state.result ? state.result.sentences : null;
      const n = rows ? rows.filter((r) => r.labels.includes(label)).length : null;
      let countText = n === null ? 'Analyze to count' : (n === 1 ? '1 sentence' : `${n} sentences`);
      els.cards.append(el('button', {
        class: 'card', type: 'button', style: `--ink-c:${INK[label]}`,
        'aria-label': `${label}. ${state.meta.explanations[label]} ${n === null ? '' : `${countText} in this document.`}`,
        onclick: () => showCategory(label, n),
      },
      el('span', { class: 'art', 'aria-hidden': 'true' },
        el('span', { class: 'symbol', text: SYMBOL[label] }),
        el('span', { class: 'ink-dot' }),
        n === null ? null : el('span', { class: 'count-badge', text: String(n) })),
      el('h3', { text: label }),
      el('p', { text: state.meta.explanations[label] }),
      el('span', { class: 'meta' },
        el('span', {}, 'Cut-off ', el('b', { text: state.meta.thresholds[label].toFixed(2) })),
        el('span', {}, n === null ? countText : el('b', { text: countText })))));
    }
  }

  function showCategory(label, n) {
    $('analyze').scrollIntoView({ behavior: 'smooth' });
    if (!state.result) {
      setStatus('Analyze a document first, then choose a category to see its sentences.');
      setMode('edit');
      return;
    }
    if (!n) {
      setStatus(`No sentence in this document is flagged as ${label}. That does not mean the document has no such clause.`);
      return;
    }
    state.filter = label;
    renderChips();
    renderResults();
    const first = visibleRows()[0];
    if (first) select(first.sentence_id, { scrollDoc: true });
  }

  // ------------------------------------------------------------------ exports
  async function exportHtml() {
    if (!state.result) return;
    try {
      download(await api('/api/export', { text: state.analyzedText }), 'clauseguard-analysis.html');
      setStatus('Downloaded the report. The file contains the text you analysed.');
    } catch (err) {
      setStatus(err.message, true);
    }
  }

  function exportJson() {
    if (!state.result) return;
    const data = { notice: state.meta.notice, thresholds: state.meta.thresholds, result: state.result };
    download(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }), 'clauseguard-analysis.json');
    setStatus('Downloaded the data. The file contains the text you analysed.');
  }

  // ------------------------------------------------------------------ example and hero
  async function loadExample() {
    try {
      const { text } = await api('/api/example');
      putText(text, 'Loaded the fictional example.');
      $('analyze').scrollIntoView({ behavior: 'smooth' });
      await runAnalysis();
    } catch (err) {
      setStatus(err.message, true);
    }
  }

  async function initSpecimen() {
    try {
      const { text } = await api('/api/example');
      const { result } = await api('/api/analyze', { text });
      const rows = result.sentences.filter((s) => s.labels.length === 1).slice(0, 3);
      if (rows.length) {
        els.specimenLines.replaceChildren(...rows.map((row) => el('li', {},
          el('span', { class: 'wash', style: `--wash:${rgba(INK[row.labels[0]], 0.17)}`, text: row.text }),
          el('span', { class: 'tags' }, row.labels.map((l) => tagEl(l))))));
        els.specimenCaption.textContent = `Read just now by model ${result.model_id.slice(0, 12)}, on this computer.`;
      }
    } catch (err) {
      els.specimenCaption.textContent = 'Start the server with python -m webapp to see the live preview.';
    }
    requestAnimationFrame(() => els.specimen.classList.add('is-live'));
  }

  // ------------------------------------------------------------------ wiring
  function wire() {
    document.addEventListener('click', (event) => {
      const target = event.target.closest('[data-action]');
      if (!target) return;
      const action = target.dataset.action;
      if (action === 'load-example') { event.preventDefault(); loadExample(); }
      else if (action === 'analyze') runAnalysis();
      else if (action === 'clear') putText('', 'Cleared. Paste new terms or open a file.');
      else if (action === 'edit') setMode('edit');
      else if (action === 'export-html') exportHtml();
      else if (action === 'export-json') exportJson();
      else if (action === 'focus-input') setTimeout(() => { if (!state.result) setMode('edit'); }, 450);
    });

    els.terms.addEventListener('input', () => {
      updateCount();
      if (state.result && els.terms.value !== state.analyzedText) {
        clearResults('Text changed. Choose Analyze terms to see results for this document.');
      }
    });
    els.terms.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) runAnalysis();
    });
    els.file.addEventListener('change', () => { readFile(els.file.files[0]); els.file.value = ''; });

    for (const type of ['dragenter', 'dragover']) {
      els.sheet.addEventListener(type, (event) => { event.preventDefault(); els.sheet.classList.add('is-dragging'); });
    }
    for (const type of ['dragleave', 'drop']) {
      els.sheet.addEventListener(type, (event) => { event.preventDefault(); els.sheet.classList.remove('is-dragging'); });
    }
    els.sheet.addEventListener('drop', (event) => readFile(event.dataTransfer.files[0]));
  }

  async function init() {
    wire();
    updateCount();
    try {
      state.meta = await api('/api/meta');
      updateCount();
      renderCards();
      const cuts = state.meta.threshold_source.startsWith('validation') ? 'one cut-off per category' : 'a fixed cut-off';
      els.modelLine.textContent = `Model ${state.meta.model_id.slice(0, 12)} (${state.meta.variant}, ${cuts}).`;
    } catch (err) {
      setStatus(err.message, true);
      els.modelLine.textContent = 'The model details could not be loaded.';
      return;
    }
    render();
    initSpecimen();
  }

  init();
})();
