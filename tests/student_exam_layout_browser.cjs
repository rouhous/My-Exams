const assert=require('node:assert/strict');
const {chromium}=require('playwright');

(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,serviceWorkers:'block'});
 const base=process.env.EXAM_BASE_URL||'http://127.0.0.1:8765';
 const page=await context.newPage();
 const errors=[];
 page.on('pageerror',error=>errors.push(error.message));

 for(const grade of [5,6]){
  await page.goto(base+'/grades5-6/index.html?grade='+grade+'&model=A&skill=listening1');
  const matrix=page.locator('.answer-matrix');
  await matrix.waitFor();
  assert.deepEqual(await matrix.locator('thead th').allTextContents(),['Text','A','B','C','D','E','F']);
  assert.equal(await matrix.locator('tbody tr').count(),5);
  assert.equal(await matrix.locator('input[type=radio]').count(),30);
  assert.equal(await page.locator('#exercise select').count(),0);
  const row=matrix.locator('tbody tr').first();
  await row.getByRole('radio',{name:'Text 1, option A'}).check();
  await row.getByRole('radio',{name:'Text 1, option B'}).check();
  assert.equal(await row.locator(':checked').count(),1);
  assert.equal(await row.locator(':checked').getAttribute('value'),'1');
  await page.reload();
  await matrix.waitFor();
  assert.equal(await row.locator(':checked').getAttribute('value'),'1');
  await page.locator('#finish').click();
  assert.match(await page.locator('#results').innerText(),/\d+ \/ 5 objective marks/);
  assert.match(await page.locator('.feedback').first().innerText(),/Item 1/);
 }
 console.log('PASS both six-option answer matrices, keyboard-accessible radios, persistence and grading');

 for(const grade of [7,8]){
  await page.goto(base+'/grades7-8/index.html?grade='+grade+'&model=A&mode=practice&skill=listening1');
  await page.locator('.pic-label').first().waitFor();
  assert.equal(await page.locator('.pic-label input[type=radio]').count(),15);
  assert(await page.locator('#examSetup').isHidden());
  assert(await page.locator('#examSession').isVisible());
  assert(!(await page.locator('#offlinePanel').getAttribute('open')));
  await page.locator('#changeExam').click();
  assert(await page.locator('#examSetup').isVisible());
  assert.equal(await page.locator('#examSetup').evaluate(element=>getComputedStyle(element).position),'static');
 }
 for(const model of 'ABCD'){
  await page.goto(base+'/grades7-8/index.html?grade=8&model='+model+'&mode=practice&skill=writing1');
  await page.locator('.survey-charts').waitFor();
  assert.equal(await page.locator('.survey-charts figure').count(),2);
  assert.equal(await page.locator('.survey-charts .mex-pie').count(),1);
  assert.deepEqual(await page.locator('.survey-charts .mex-category').allTextContents(),['Yes','No','Not sure']);
  assert.equal(await page.locator('.survey-charts .mex-pie-item').count(),4);
  await page.locator('textarea[data-k="writing1:text"]').fill('The survey asked one hundred students.');
  assert.match(await page.locator('#words_writing1').innerText(),/6 words · minimum 80/);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth===innerWidth));
 }
 console.log('PASS Grades 7–8 scrolling and picture radio controls, and two charts in all four Grade 8 models');

 for(const unit of [1,2,3]){
  await page.goto(base+'/grade9/unit-exams/index.html?unit='+unit+'&mode=skill&skill=0&open=1');
  await page.locator('#paper.active').waitFor();
  const images=page.locator('.images img');
  assert.equal(await images.count(),15);
  assert(await page.locator('#setup').isHidden());
  assert.equal(await page.locator('.images .choice input[type="radio"]').count(),15);
  await page.waitForFunction(()=>[...document.querySelectorAll('.images img')].every(img=>img.naturalWidth>0&&img.currentSrc.endsWith('.webp')));
  assert.match(await page.locator('audio').getAttribute('src'),/two-pass\.mp3$/);
 }
 console.log('PASS illustrated Grade 9 activities open directly in all three units');

 const tracks=[
  ['/grade-skills.html?grade=11&track=core','Grammar',4],
  ['/grade-skills.html?grade=11&track=elective','Listening 2',4],
  ['/grade12-skills.html?track=12-core','Reading 2',4],
  ['/grade12-skills.html?track=12-elective','Writing 2',4]
 ];
 for(const [path,skill,units] of tracks){
  for(let unit=0;unit<units;unit++){
   await page.goto(base+path);
   await page.locator('#unit').selectOption(String(unit));
   await page.getByRole('link',{name:'بدء '+skill,exact:true}).click();
   await page.locator('#paper.active .part').waitFor();
   assert(await page.locator('#setup').isHidden());
   assert.equal(await page.locator('#paper.active .part').count(),1);
   assert.match(await page.locator('.part h2').innerText(),new RegExp(skill));
  }
 }
 for(const [grade,href,section] of [
  [5,'/grades5-6/index.html?grade=5&model=A&skill=reading2','#exercise'],
  [6,'/grades5-6/index.html?grade=6&model=A&skill=reading1','#exercise'],
  [7,'/grades7-8/index.html?grade=7&model=A&mode=practice&skill=reading2','#exercise'],
  [8,'/grades7-8/index.html?grade=8&model=A&mode=practice&skill=reading2','#exercise'],
  [9,'/grade9/unit-exams/index.html?unit=1&mode=skill&skill=4&open=1','#tasks'],
  [10,'/grade10/index.html?model=A&mode=practice&skill=reading2','#exam'],
  [11,'/grade11/core/units/paper-a-preview.html?mode=skill&skill=rdg2&open=1','#sections'],
  [12,'/grade12/elective/units/paper-a-preview.html?unit=1&mode=skill&skill=rdg2&open=1','#sections']
 ]){
  await page.goto(base+href);
  const panes=page.locator(section+' .exam-dual-panel:visible');
  await panes.first().waitFor();
  assert.equal(await panes.count(),2);
  assert(await panes.evaluateAll(els=>els.every(e=>getComputedStyle(e).overflowY==='auto')));
  assert.equal(await page.locator('input[placeholder="Student name"], input[name^="student-"], #exercise .cover').count(),0,'Cover on grade '+grade);
 }
 console.log('PASS two independently scrollable panes for Reading in Grades 5–12');

 await page.goto(base+'/grades7-8/index.html?grade=7&model=A&mode=practice&skill=reading1');
 const letterFields=page.locator('.exam-letter-row input');
 await letterFields.first().waitFor();
 assert.equal(await letterFields.count(),5);
 const answerLetters=await page.evaluate(()=>JSON.parse(document.getElementById('DATA').textContent)
   .find(m=>m.grade===7&&m.model==='A').sections.find(s=>s.key==='reading1').answers
   .map((answer,i)=>String.fromCharCode((i%2 ? 65 : 97)+answer)));
 for(let i=0;i<answerLetters.length;i++) await letterFields.nth(i).fill(answerLetters[i]);
 await page.locator('#submit').click();
 assert.equal(await page.locator('.exam-letter-cell[data-verdict=correct]').count(),5);

 await page.goto(base+'/grade9/unit-exams/index.html?unit=1&mode=skill&skill=3&open=1');
 await page.locator('.exam-letter-row input').first().waitFor();
 assert.equal(await page.locator('.exam-letter-row input').count(),4);
 assert.equal(await page.locator('.exam-matching .exam-dual-panel').count(),2);

 await page.goto(base+'/mixed-exams/index.html?grade=8&mode=exam');
 await page.locator('[data-student-sheet]').waitFor();
 assert.equal(await page.locator('[data-exam-page]:visible').count(),1);
 assert(await page.locator('#clock').isHidden());
 await page.locator('input[name="student-name"]').fill('Sample learner');
 const next=page.getByRole('button',{name:'Next page',exact:true});
 const previous=page.getByRole('button',{name:'Previous page',exact:true});
 await next.click();
 await page.locator('#listening1').waitFor();
 const firstPicture=page.locator('#listening1 input[type=radio]').first();
 await firstPicture.check();
 await next.click();
 assert(await page.locator('#listening2').isVisible());
 assert(await page.locator('#listening1').isHidden());
 await previous.click();
 assert(await firstPicture.isChecked());
 await page.reload();
 await firstPicture.waitFor();
 assert(await firstPicture.isChecked());
 for(let i=0;i<4;i++)await next.click();
 assert(await page.locator('#reading1').isVisible());
 assert.equal(await page.locator('#reading1 .exam-letter-row input').count(),5);
 await page.setViewportSize({width:1200,height:800});
 assert(await page.locator('#reading1 .exam-dual-panel').evaluateAll(els=>
   els.length===2 && Math.abs(els[0].getBoundingClientRect().top-els[1].getBoundingClientRect().top)<2));
 await page.setViewportSize({width:390,height:844});
 console.log('PASS numbered matching, case-insensitive marking, and one-page navigation with restoration');

 await page.goto(base+'/grade12-skills.html?track=12-core');
 await page.locator('#skills a').first().waitFor();
 assert.equal(await page.locator('.ex-tools,.ex-ink,.ex-note').count(),0);
 assert(await page.evaluate(()=>document.documentElement.scrollHeight-Math.round(document.querySelector('footer').getBoundingClientRect().bottom+scrollY)<4));
 assert.deepEqual(errors,[]);
 console.log('PASS direct entry for all 16 upper-grade unit/track combinations and Grade 12 footer');
 await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
