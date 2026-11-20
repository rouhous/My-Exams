const { checkMixed } = require('./check_mixed_browser.cjs');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:420,height:850}});
 const page=await context.newPage();
 page.on('pageerror',e=>console.error('PAGE ERROR',e.message));
 await page.goto('http://127.0.0.1:8765/grade10/index.html',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>!document.querySelector('#start').disabled,null,{timeout:30000});
 for(const model of 'ABCD'){
  await page.selectOption('#model',model);
  await page.click('#start');
  const sections=await page.locator('#exam section.section').count();
  if(sections!==7)throw Error('Grade 10 model '+model+' has '+sections+' sections');
  const objs=await page.locator('#exam .question').count();
  if(objs!==45)throw Error('Grade 10 model '+model+' objective questions '+objs+' !=45');
  const audio=await page.locator('#exam audio').count();
  if(audio!==1)throw Error('Grade 10 model '+model+' missing audio player');

 }
 await page.selectOption('#mode','practice');
 await page.selectOption('#skill','reading2');
 await page.click('#start');
 if(await page.locator('#exam section.section').count()!==1)throw Error('Single-skill practice failed');
 if((await page.locator('#clock').textContent())!=='Untimed')throw Error('Practice should not be timed');
 await checkMixed(page.context(),'grade10/index.html',{},{sections:7,items:45,marks:60});
 await browser.close();console.log('PASS Grade 10 A–D (45 objective+2 writing), corrected four-unit reading, mixed audio provenance, random and untimed skills');
})().catch(e=>{console.error(e);process.exit(1)});
