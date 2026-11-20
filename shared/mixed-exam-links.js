/* Keep older exam bookmarks and full-paper controls on the same question bank. */
(() => {
  'use strict';
  const script = document.currentScript;
  const source = script.dataset.examSource;
  const params = new URLSearchParams(location.search);
  const config = {
    foundations: ['startExam', 'randomExam'],
    middle: ['start', 'randomNew'],
    '9': ['start'],
    '9-archive': ['start'],
    '10': ['start', 'random'],
    '11-core': ['start', 'random'],
    upper: ['start']
  }[source];
  const $ = id => document.getElementById(id);

  function selection(usePage) {
    const pick = id => (usePage ? $(id)?.value : params.get(id)) || '';
    const [partGrade, partTrack] = (source === 'upper' ? pick('track') : source).split('-');
    const grade = source === 'foundations' || source === 'middle'
      ? Number(pick('grade') || (source === 'foundations' ? 5 : 7)) : Number(partGrade);
    return { grade, track: partTrack, model: pick('model'), mode: pick('mode') };
  }

  function mixedModel(grade, model) {
    return Boolean(model) && (grade >= 10 || grade === 5 ? /^[EF]$/ : /^[DEFR]$/).test(model);
  }

  function open({ grade, track }, random, replace) {
    if (!Number.isInteger(grade) || grade < 5 || grade > 12) return;
    if (grade >= 11 && !['core', 'elective'].includes(track)) return;
    const url = new URL('../mixed-exams/index.html', script.src);
    url.searchParams.set('grade', grade);
    if (grade >= 11) url.searchParams.set('track', track);
    url.searchParams.set('mode', random ? 'random' : 'exam');
    if (replace) location.replace(url.href);
    else location.assign(url.href);
  }

  const incoming = selection(false);
  if (incoming.mode === 'random' || incoming.mode === 'mixed' ||
      ['exam', 'full'].includes(incoming.mode) && !params.has('skill') && mixedModel(incoming.grade, incoming.model)) {
    open(incoming, incoming.mode === 'random', true);
  }

  document.addEventListener('click', event => {
    const button = event.target.closest('button');
    if (!button || !config.includes(button.id)) return;
    const current = selection(true);
    const random = button.id === config[1] || current.mode === 'random' || current.model === 'R';
    const comprehensive = current.mode === 'mixed' ||
      !['practice', 'skill'].includes(current.mode) && mixedModel(current.grade, current.model);
    if (!random && !comprehensive) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    open(current, random, false);
  }, true);
})();
