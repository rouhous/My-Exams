(() => {
  'use strict';

  const $ = id => document.getElementById(id);
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const params = new URLSearchParams(location.search);
  const grade = Number(params.get('grade'));
  const track = params.get('track');
  const randomExam = params.get('mode') === 'random';
  const scope = grade < 11 ? String(grade) : grade + '-' + track;
  const newSeed = () => crypto.getRandomValues(new Uint32Array(1))[0];
  const validSeed = /^\d{1,10}$/.test(params.get('seed') || '') && Number(params.get('seed')) <= 0xffffffff;
  const seed = randomExam ? (validSeed ? Number(params.get('seed')) : newSeed()) : 20261120;
  const title = randomExam ? 'Random exam' : 'Comprehensive exam';
  const storageKey = 'my-exams-mixed-v1:' + scope + ':' + (randomExam ? 'random-' : 'fixed-') + seed;
  const cachedPaper = 'my-exams-downloaded-papers-v1';
  let state = { started: Date.now(), answers: {}, finished: false };
  let sections = [], interval = 0, bank;
  const assessed = [];
  const media = new Set();

  function escape(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  }

  function titleFor(key) {
    return key[0].toUpperCase() + key.slice(1).replace(/(\d+)$/, ' $1');
  }

  function file(path) {
    media.add('../' + path);
    return escape('../' + path);
  }

  function shortInput(id, q) {
    const label = q.maxWords ? 'Short answer · up to ' + q.maxWords + ' words' : 'Short answer';
    return '<input type="text" name="' + id + '" aria-label="' + label + '" placeholder="' + label + '" maxlength="250">';
  }

  function radio(id, i, label) {
    return '<input type="radio" name="' + id + '" value="' + i + '" aria-label="' + escape(label) + '">';
  }

  function renderOptions(q, id) {
    if (!q.options) return shortInput(id, q);
    if (q.images) return '<div class="image-options">' + q.images.map((src, i) =>
      '<label class="answer"><b>' + letters[i] + '</b><img src="' + file(src) + '" alt="Picture ' + letters[i] + '">' +
      radio(id, i, 'Option ' + letters[i]) + '</label>').join('') + '</div>';
    return '<div class="answers">' + q.options.map((label, i) =>
      '<label class="answer">' + radio(id, i, label) + '<span>' + letters[i] + '. ' + escape(label) + '</span></label>').join('') + '</div>';
  }

  function renderQuestion(q, i, s) {
    const id = s.key + '-' + (i + 1);
    assessed.push({ id, q, skill: s.key });
    return '<div class="question" id="' + id + '-item" data-unit="' + q.source.unit + '">' +
      (q.passage ? '<div class="passage">' + escape(q.passage) + '</div>' : '') +
      '<h3>' + (i + 1) + '. ' + escape(q.stem) + '</h3>' +
      (q.picture ? '<img class="stem-image" src="' + file(q.picture) + '" alt="Picture for item ' + (i + 1) + '">' : '') +
      renderOptions(q, id) + '</div>';
  }

  function renderGrid(s) {
    const { kind, options } = s.grid;
    const gallery = kind === 'images'
      ? '<div class="image-options">' + options.map((src, i) =>
        '<figure><figcaption>' + letters[i] + '</figcaption><img src="' + file(src) + '" alt="Illustration ' + letters[i] + '"></figure>').join('') + '</div>'
      : '<ol class="words">' + options.map((word, i) => '<li><b>' + letters[i] + '</b> ' + escape(word) + '</li>').join('') + '</ol>';
    let prompts = '';
    if (s.key !== 'listening1') {
      prompts = '<ol>' + s.questions.map((q, i) => '<li>' + (q.picture
        ? '<img class="stem-image" src="' + file(q.picture) + '" alt="Picture for item ' + (i + 1) + '">'
        : escape(q.stem)) + '</li>').join('') + '</ol>';
    }
    const head = '<thead><tr><th scope="col">Item</th>' +
      options.map((_, i) => '<th scope="col">' + letters[i] + '</th>').join('') + '</tr></thead>';
    const rows = s.questions.map((q, i) => {
      const id = s.key + '-' + (i + 1);
      assessed.push({ id, q, skill: s.key });
      return '<tr id="' + id + '-item" data-unit="' + q.source.unit + '"><th scope="row">' + (i + 1) + '</th>' +
        options.map((_, j) => '<td><label>' + radio(id, j, 'Item ' + (i + 1) + ', option ' + letters[j]) + '</label></td>').join('') + '</tr>';
    }).join('');
    return gallery + prompts + '<table class="answer-grid" aria-label="Shade one answer for each item">' + head + '<tbody>' + rows + '</tbody></table>';
  }

  function renderWriting(task) {
    const figures = [...(task.survey || []), ...(task.chart ? [task.chart] : [])];
    const charts = figures.map(c => window.MyExamsCharts.render(c)).join('');
    const facts = task.facts ? '<ul>' + task.facts.map(x => '<li>' + escape(x) + '</li>').join('') + '</ul>' : '';
    const images = (task.images || []).map((src, i) => '<img class="stem-image" src="' + file(src) + '" alt="Writing picture ' + (i + 1) + '">').join('');
    return '<div class="writing-task" data-unit="' + task.unit + '">' + charts + facts + images +
      '<p class="prompt">' + escape(task.prompt) + '</p><textarea name="' + task.key + '" data-writing data-min-words="' +
      escape(task.minWords || '') + '" aria-label="Write your answer"></textarea><p id="' + task.key + '-words"></p></div>';
  }

  function renderSection(s) {
    const device = s.audio ? '<p>Listen to texts 1–5, then listen to the same texts again.</p><button type="button" id="' + s.key +
      '-prepare">Prepare recording</button><p id="' + s.key + '-audio-status" role="status"></p><audio controls hidden></audio>' : '';
    s.audio?.forEach(({ path }) => file(path));
    let i = 0;
    const content = s.writing ? renderWriting(s.writing)
      : s.grid ? renderGrid(s)
      : s.groups ? s.groups.map(({ source, questions }, n) => '<div class="source-group"><h3>' +
          (source.audio ? 'Recording ' : 'Text ') + letters[n] + '</h3>' +
          (source.audio ? '<audio controls preload="none" src="' + file(source.audio) + '"></audio>'
            : '<div class="passage">' + escape(source.passage) + '</div>') +
          questions.map(q => renderQuestion(q, i++, s)).join('') + '</div>').join('')
      : s.questions.map(q => renderQuestion(q, i++, s)).join('');
    return '<section class="exam-part" id="' + s.key + '"><h2>' + titleFor(s.key) + '<small>' + s.marks + ' marks</small></h2>' +
      device + content + '</section>';
  }

  const sampleRate = 24000;

  function wave(clips) {
    const length = clips.reduce((total, c) => total + c.samples.length + c.pause, 0);
    const buffer = new ArrayBuffer(44 + 2 * length);
    const header = new DataView(buffer);
    for (const [offset, label] of [[0, 'RIFF'], [8, 'WAVE'], [12, 'fmt '], [36, 'data']]) {
      for (let i = 0; i < label.length; i++) header.setUint8(offset + i, label.charCodeAt(i));
    }
    header.setUint32(4, buffer.byteLength - 8, true);
    header.setUint32(16, 16, true);
    header.setUint16(20, 1, true);
    header.setUint16(22, 1, true);
    header.setUint32(24, sampleRate, true);
    header.setUint32(28, sampleRate * 2, true);
    header.setUint16(32, 2, true);
    header.setUint16(34, 16, true);
    header.setUint32(40, 2 * length, true);
    let offset = 44;
    for (const { samples, pause } of clips) {
      for (const s of samples) {
        header.setInt16(offset, Math.max(-32768, Math.min(32767, s * 32767)), true);
        offset += 2;
      }
      offset += pause * 2;
    }
    return new Blob([buffer], { type: 'audio/wav' });
  }

  async function prepareAudio(section) {
    const button = $(section.key + '-prepare');
    const status = $(section.key + '-audio-status');
    button.disabled = true;
    status.textContent = 'Preparing the recording…';
    try {
      const Decoder = window.OfflineAudioContext || window.webkitOfflineAudioContext;
      const ctx = new Decoder(1, 1, sampleRate);
      const paths = [...new Set(section.audio.map(clip => clip.path))];
      const decoded = new Map(await Promise.all(paths.map(async path => {
        const response = await fetch('../' + path);
        if (!response.ok) throw Error('Recording unavailable');
        const buffer = await ctx.decodeAudioData(await response.arrayBuffer());
        return [path, buffer.getChannelData(0)];
      })));
      const clips = section.audio.map(({path, range, pause}) => ({
        samples: decoded.get(path).subarray(Math.round(range[0] * sampleRate), Math.round(range[1] * sampleRate)),
        pause: Math.round(pause * sampleRate)
      }));
      const audio = $(section.key).querySelector('audio');
      audio.src = URL.createObjectURL(wave(clips));
      audio.hidden = false;
      button.hidden = true;
      status.textContent = 'Recording ready. Press play to begin.';
    } catch {
      status.textContent = 'The recording could not be prepared. Try again after checking your connection.';
      button.disabled = false;
    }
  }

  function persist() {
    try { sessionStorage.setItem(storageKey, JSON.stringify(state)); } catch {}
  }

  function countWords(area) {
    const count = area.value.trim().split(/\s+/).filter(Boolean).length;
    $(area.name + '-words').textContent = count + ' words' + (area.dataset.minWords ? ' · minimum ' + area.dataset.minWords : '');
  }

  function restore() {
    try {
      const saved = JSON.parse(sessionStorage.getItem(storageKey));
      if (saved && Number.isFinite(saved.started) && saved.answers) state = saved;
    } catch {}
    for (const input of $('paper').querySelectorAll('input, textarea')) {
      const saved = state.answers[input.name];
      if (input.type === 'radio') input.checked = input.value === saved;
      else input.value = saved || '';
      if (input.tagName === 'TEXTAREA') countWords(input);
    }
    persist();
  }

  function finish(expired = false, move = true) {
    clearInterval(interval);
    state.finished = true;
    persist();
    $('finish').disabled = true;
    $('paper').querySelectorAll('input').forEach(input => { input.disabled = true; });
    $('paper').querySelectorAll('textarea').forEach(area => { area.readOnly = true; });
    let correct = 0, unanswered = 0;
    for (const { id, q, skill } of assessed) {
      const selected = state.answers[id] || '';
      const okay = selected.trim() && (q.options
        ? Number(selected) === q.answer
        : window.MyExamsShortAnswers.evaluate(selected, q).correct);
      if (okay) correct++;
      if (!selected.trim()) unanswered++;
      const item = $(id + '-item');
      item.dataset.verdict = okay ? 'correct' : 'incorrect';
      const override = q.target && q.source.grid === 'images' ? letters[q.answer] : undefined;
      const context = { skill, passage: q.passage || q.source.passage, script: q.script || q.source.script };
      const feedback = window.MyExamsLearning.feedback(q, context, Boolean(okay), override);
      if (item.tagName === 'TR') {
        const review = item.parentElement.insertRow(item.sectionRowIndex + 1);
        review.insertCell().colSpan = item.cells.length;
        review.cells[0].innerHTML = feedback;
      } else {
        item.insertAdjacentHTML('beforeend', feedback);
      }
    }
    const result = $('result');
    result.hidden = false;
    result.innerHTML = '<h2>' + (expired ? 'Time is up' : 'Exam review') + '</h2><p><strong>' + correct + ' / ' + assessed.length +
      '</strong> automatically marked · ' + unanswered + ' unanswered.</p><p>Writing tasks are marked separately.</p>';
    if (!randomExam) $('retry').hidden = false;
    if (move) result.focus();
  }

  function tick(move = true) {
    const seconds = Math.max(0, Math.ceil((state.started + bank.minutes * 60000 - Date.now()) / 1000));
    $('clock').textContent = [Math.floor(seconds / 3600), Math.floor(seconds / 60) % 60, seconds % 60].map(n =>
      String(n).padStart(2, '0')).join(':');
    if (!seconds && !state.finished) finish(true, move);
  }

  async function download() {
    const button = $('download');
    const status = $('downloadState');
    button.disabled = true;
    try {
      const cache = await caches.open(cachedPaper);
      const assets = [location.href, './' + scope + '.json', './paper.css', './paper.js', './assemble.js',
        '../shared/oman-theme.css?v=29', '../shared/short-answer-marking.js',
        '../shared/data-charts.js', '../shared/learning-feedback.js?v=1', ...media];
      let done = 0;
      for (const asset of assets) {
        const url = new URL(asset, location.href);
        const response = await fetch(url);
        if (!response.ok) throw Error('File unavailable');
        await cache.put(url, response);
        status.textContent = 'Downloading ' + ++done + ' / ' + assets.length;
      }
      status.textContent = 'This paper is ready for offline use on this device.';
    } catch {
      status.textContent = 'The download did not finish. Try again while online.';
    } finally {
      button.disabled = false;
    }
  }

  async function init() {
    if (!/^(?:[5-9]|10|1[12]-(?:core|elective))$/.test(scope)) throw Error('Choose a grade from the exam portal.');
    const query = new URLSearchParams({ grade: String(grade), mode: randomExam ? 'random' : 'exam' });
    if (grade >= 11) query.set('track', track);
    if (randomExam) {
      $('newPaper').href = '?' + query.toString();
      $('newPaper').hidden = false;
      query.set('seed', String(seed));
      if (!validSeed) history.replaceState(null, '', '?' + query.toString());
    }
    $('gradeLink').href = grade === 12 ? '../grade12-skills.html?track=' + track
      : '../grade-skills.html?grade=' + grade + (grade === 11 ? '&track=' + track : '');
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('../sw.js', { updateViaCache: 'none' }).catch(() => {});
    const response = await fetch('./' + scope + '.json');
    if (!response.ok) throw Error('The question bank could not be loaded. Reload the page to try again.');
    bank = await response.json();
    sections = window.MyExamsMixed.build(bank, seed);
    $('title').textContent = title + ' · Grade ' + grade + (grade >= 11 ? ' ' + titleFor(track) : '');
    document.title = $('title').textContent + ' | My Exams';
    $('paperMarks').textContent = bank.marks + ' marks · ' + bank.minutes + ' minutes';
    $('skills').innerHTML = sections.map(s => '<a href="#' + s.key + '">' + titleFor(s.key) + '</a>').join('');
    $('paper').innerHTML = sections.map(renderSection).join('');
    $('paper').addEventListener('submit', e => e.preventDefault());
    $('paper').addEventListener('play', event => {
      for (const audio of $('paper').querySelectorAll('audio')) {
        if (audio !== event.target && !audio.paused) audio.pause();
      }
    }, true);
    $('paper').addEventListener('input', event => {
      if (state.finished || !event.target.name) return;
      state.answers[event.target.name] = event.target.value;
      if (event.target.tagName === 'TEXTAREA') countWords(event.target);
      persist();
    });
    sections.filter(s => s.audio).forEach(s => { $(s.key + '-prepare').onclick = () => prepareAudio(s); });
    $('download').onclick = download;
    $('finish').onclick = () => finish();
    $('retry').onclick = () => {
      state = { started: Date.now(), answers: {}, finished: false };
      persist();
      location.reload();
    };
    $('status').hidden = true;
    $('session').hidden = false;
    restore();
    tick(false);
    if ($('finish').disabled) return;
    if (state.finished) finish(false, false);
    else interval = setInterval(tick, 1000);
  }

  init().catch(error => { $('status').textContent = error.message; });
})();
