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
 await page.goto(base+'/grade12-skills.html?track=12-core');
 await page.locator('#skills a').first().waitFor();
 assert.equal(await page.locator('.ex-tools,.ex-ink,.ex-note').count(),0);
 assert(await page.evaluate(()=>document.documentElement.scrollHeight-Math.round(document.querySelector('footer').getBoundingClientRect().bottom+scrollY)<4));
 assert.deepEqual(errors,[]);
 console.log('PASS direct entry for all 16 upper-grade unit/track combinations and Grade 12 footer');
 await browser.close();
})().catch(error=>{console.error(error);process.exit(1)});
