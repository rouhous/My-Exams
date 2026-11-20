/* Shared assembly for the fixed semester review and seeded random papers. */
(function (root) {
  'use strict';

  function random(seed) {
    let state = seed >>> 0;
    return () => {
      state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
      return state / 4294967296;
    };
  }

  function shuffle(values, rng) {
    const items = values.slice();
    for (let i = items.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [items[i], items[j]] = [items[j], items[i]];
    }
    return items;
  }

  function normalized(text) {
    return String(text || '').trim().toLowerCase().replace(/\s+/g, ' ');
  }

  function identity(q, source) {
    if (q.point) return q.point;
    if (source.key === 'vocabulary' && q.options) return normalized(q.options[q.answer]);
    return q.target || q.picture || normalized([q.passage || source.passage, q.stem].filter(Boolean).join('\n'));
  }

  function orderedSources(sources, count, rng) {
    const order = shuffle(sources, rng);
    return Array.from({ length: count }, (_, i) => order[i % order.length]);
  }

  function select(sources, rng) {
    const template = sources[0];
    const isNumbered = Boolean(template.timing);
    const planned = shuffle(sources, rng);
    const perUnit = new Map(planned.map((source, i) => [
      source.unit, Math.floor(template.marks / planned.length) + Number(i < template.marks % planned.length)
    ]));
    const used = new Set();
    const results = [];
    const slots = Array.from({ length: template.marks }, (_, i) => template.questions[i]);
    const candidates = slots.map((slot, index) => {
      const kind = ['grammar', 'vocabulary'].includes(template.key) ? null : slot?.kind;
      const first = index % planned.length;
      return [...planned.slice(first), ...planned.slice(0, first)].flatMap(source => {
        const entries = isNumbered
          ? [{ q: source.questions[index], i: index }]
          : shuffle(source.questions.map((q, i) => ({ q, i })), rng);
        return entries.filter(({ q }) => q && (!kind || q.kind === kind))
          .map(({ q, i }) => ({ q, i, source, id: identity(q, source) }));
      });
    });
    const order = slots.map((_, i) => i).sort((a, b) => candidates[a].length - candidates[b].length);

    function fill(depth) {
      if (depth === slots.length) return true;
      const index = order[depth];
      for (const { q, i, source, id } of candidates[index]) {
        const remaining = perUnit.get(source.unit);
        if (!remaining || used.has(id)) continue;
        used.add(id);
        perUnit.set(source.unit, remaining - 1);
        results[index] = { ...q, source, sourceIndex: i };
        if (fill(depth + 1)) return true;
        perUnit.set(source.unit, remaining);
        used.delete(id);
      }
      return false;
    }

    if (!fill(0)) throw Error('Unable to assemble ' + template.key + ' across all units.');
    return results;
  }

  function gridFor(sources, questions, rng) {
    const count = sources[0].options.length;
    const targets = questions.map(q => q.target);
    const distractors = [...new Set(sources.flatMap(s => s.options))].filter(option => !targets.includes(option));
    const options = shuffle([...targets, ...shuffle(distractors, rng).slice(0, count - targets.length)], rng);
    return { kind: sources[0].grid, options };
  }

  function groupBySource(questions) {
    const groups = new Map();
    for (const q of questions) {
      if (!groups.has(q.source.unit)) groups.set(q.source.unit, { source: q.source, questions: [] });
      groups.get(q.source.unit).questions.push(q);
    }
    return [...groups.values()].map(group => ({
      ...group, questions: group.questions.sort((a, b) => a.sourceIndex - b.sourceIndex)
    }));
  }

  function build(bank, seed) {
    const rng = random(seed);
    const writingOrder = orderedSources(bank.units, 2, rng);
    return bank.units[0].sections.map((template, index) => {
      const sources = bank.units.map(u => ({ ...u.sections[index], unit: u.unit }));
      const key = template.key;
      if (key.startsWith('writing')) {
        const source = sources.find(s => s.unit === writingOrder[Number(key.slice(-1)) - 1].unit);
        return { key, marks: template.marks, writing: source };
      }
      const selected = select(sources, rng);
      const grid = template.grid ? gridFor(sources, selected, rng) : null;
      for (const q of selected) {
        if (grid) {
          q.options = grid.options;
          q.answer = q.options.indexOf(q.target);
        } else if (q.options && q.kind !== 'tf' && q.kind !== 'match') {
          const order = shuffle(q.options.map((_, i) => i), rng);
          q.options = order.map(i => q.options[i]);
          if (q.images) q.images = order.map(i => q.images[i]);
          q.answer = order.indexOf(q.answer);
        }
      }
      const groups = !template.timing && (template.audio || template.passage) ? groupBySource(selected) : null;
      const questions = groups ? groups.flatMap(g => g.questions) : selected;
      const audio = template.timing ? numberedAudio(questions) : null;
      return { key, marks: template.marks, questions, groups, grid, audio };
    });
  }

  function numberedAudio(questions) {
    const first = questions[0].source;
    const tracks = questions.map(({ source, sourceIndex }) => ({
      path: source.audio, range: source.timing.items[sourceIndex], pause: 3
    }));
    return [
      { path: first.audio, range: first.timing.intro, pause: 3 },
      ...tracks,
      { path: first.audio, range: first.timing.repeat, pause: 2 },
      ...tracks
    ];
  }

  root.MyExamsMixed = { build };
})(typeof window === 'undefined' ? globalThis : window);
