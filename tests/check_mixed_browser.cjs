const assert = require('node:assert/strict');

exports.checkMixed = async function checkMixed(context, legacyPath, query, expected) {
  const page = await context.newPage();
  const prefix = 'http://127.0.0.1:8765/';
  try {
    for (const mode of ['exam', 'random']) {
      const params = new URLSearchParams({ ...query, model: 'E', mode: mode === 'exam' && query.track ? 'full' : mode, open: '1' });
      await page.goto(prefix + legacyPath + '?' + params, { waitUntil: 'commit' });
      await page.waitForURL('**/mixed-exams/index.html?**');
      await page.locator('[data-student-sheet]').waitFor({ state: 'visible' });
      assert.equal(await page.locator('.exam-part:not([data-student-sheet])').count(), expected.sections);
      const actual = await page.evaluate(() => ({
        questions: document.querySelectorAll('#paper .question').length,
        allUnits: [...document.querySelectorAll('#paper .exam-part:not([data-student-sheet])')].map(section =>
          new Set([...section.querySelectorAll('.question')].map(item => item.dataset.unit)).size),
        writing: [...document.querySelectorAll('.writing-task')].map(item => item.dataset.unit)
      }));
      assert.equal(actual.questions, expected.items);
      assert(actual.allUnits.slice(0, -2).every(n => n === 4));
      assert.equal(new Set(actual.writing).size, 2);
      assert.match(await page.locator('#paperMarks').textContent(), new RegExp(expected.marks + ' marks'));
    }
  } finally {
    await page.close();
  }
};
