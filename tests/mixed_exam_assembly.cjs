const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const directory = path.join(__dirname, '..', 'mixed-exams');
require(path.join(directory, 'assemble.js'));

for (const file of fs.readdirSync(directory).filter(name => /^\d.*\.json$/.test(name))) {
  const bank = JSON.parse(fs.readFileSync(path.join(directory, file)));
  const variants = new Set();
  for (const seed of [20261120, ...Array.from({ length: 100 }, (_, i) => 1 + i * 356071)]) {
    const paper = MyExamsMixed.build(bank, seed);
    assert.equal(paper.reduce((n, section) => n + section.marks, 0), bank.marks);
    assert.equal(new Set(paper.filter(section => section.writing).map(section => section.writing.unit)).size, 2);

    for (const section of paper.filter(part => part.questions)) {
      const { questions } = section;
      assert.equal(questions.length, section.marks);
      const count = bank.units.map(unit => questions.filter(q => q.source.unit === unit.unit).length);
      assert(count.every(n => n > 0) && Math.max(...count) - Math.min(...count) <= 1, file + ': ' + section.key);
      if (section.key === "grammar") assert.equal(new Set(questions.map(q => q.point)).size, questions.length);
      for (const q of questions) {
        const original = q.source.questions[q.sourceIndex];
        if (section.grid) assert.equal(q.options[q.answer], q.target);
        else if (q.options) assert.equal(q.options[q.answer], original.options[original.answer]);
        if (q.images) assert.equal(q.images[q.answer], original.images[original.answer]);
      }
      for (const group of section.groups || []) {
        assert(group.questions.every(q => q.source === group.source));
      }
      if (section.audio) {
        assert.equal(section.audio.length, 12);
        assert.deepEqual(section.audio.slice(1, 6), section.audio.slice(7));
        for (let index = 0; index < 5; index++) {
          const item = questions[index];
          assert.equal(item.sourceIndex, index);
          assert.deepEqual(section.audio[index + 1].range, item.source.timing.items[index]);
        }
      }
    }
    variants.add(JSON.stringify(paper.map(section => section.writing?.unit ||
      section.questions.map(q => [q.source.unit, q.sourceIndex]))));
  }
  assert(variants.size > 75);
  console.log('Balanced question selection, answer keys and listening sources:', file);
}
