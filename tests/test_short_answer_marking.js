/* Regression tests for Grade 12 Reading 1 and other WH tasks. */
const fs=require('fs');
const assert=require('assert');
const source=fs.readFileSync('shared/short-answer-marking.js','utf8');
const w={};new Function('window',source)(w);
const grade=w.MyExamsShortAnswers;
const questions=JSON.parse(fs.readFileSync('grade12/elective/units/unit1-reading1-original-draft.json','utf8')).questions;
const grade7=JSON.parse(fs.readFileSync('grades7-8/activities.json','utf8')).find(m=>m.id==='g7-a').sections.find(s=>s.key==='reading2');
const illness=grade7.items.find(q=>q.stem==='Why did the team change their interview plan?');
assert(grade.evaluate('their guest became ill.',illness).correct,'Accept the source-supported wording used in the screenshot');
assert.strictEqual(questions.length,12);
for(const q of questions){
 const r=grade.evaluate(q.answer,q);
 assert(r.correct,'Expected auto-correct for '+q.answer);
 assert(r.wordCount<=r.permitted);
}
const sample=questions[11];
assert(grade.evaluate('Students made an attendance list for participants',sample).correct);
assert(!grade.evaluate('Students prepared the official complete workshop attendance list for all new participants',sample).correct);
assert(!grade.evaluate('a guest register',sample).correct);
assert(grade.evaluate('180 OMR',questions[5]).correct);
assert(grade.evaluate('THE COMMUNITY LIBRARY.',questions[3]).correct);
assert(!grade.evaluate('',sample).correct);
assert(grade.evaluate('an attendance list',sample).correct);
console.log('PASS 12 Grade-12 Reading 1 short answers, +4 words, over-limit, wrong, empty and punctuation tests');
