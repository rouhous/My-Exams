const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:420,height:850}});
 page.on('pageerror',e=>console.error('PAGE ERROR',e.message));
 await page.goto('http://127.0.0.1:8765/grade10/index.html',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.querySelector('#intro').textContent.includes('Six review models'),null,{timeout:30000});
 for(const model of 'ABCDEF'){
  await page.selectOption('#model',model);
  await page.click('#start');
  const sections=await page.locator('#exam section.section').count();
  if(sections!==7)throw Error('Grade 10 model '+model+' has '+sections+' sections');
  const objs=await page.locator('#exam .question').count();
  if(objs!==45)throw Error('Grade 10 model '+model+' objective questions '+objs+' !=45');
  const audio=await page.locator('#exam audio').count();
  if(audio!==1)throw Error('Grade 10 model '+model+' missing audio player');
  const src=await page.locator('#exam audio').first().getAttribute('src');
  if(model==='E'||model==='F'){
   const expected=model==='E'?'g10-a-listening.mp3':'g10-d-listening.mp3';
   if(!src.includes(expected))throw Error('Comprehensive source listening mismatch: '+src+' != '+expected);
  }
 }
 await page.click('#random');
 if(await page.locator('#exam section.section').count()!==7)throw Error('Grade 10 random exam incomplete');
 const models=await page.evaluate(()=>document.querySelector('#intro').textContent);
 if(!models.includes('Random complete semester'))throw Error('Random model never activated');
 await page.selectOption('#mode','practice');
 await page.selectOption('#skill','reading2');
 await page.click('#start');
 if(await page.locator('#exam section.section').count()!==1)throw Error('Single-skill practice failed');
 if((await page.locator('#clock').textContent())!=='Untimed')throw Error('Practice should not be timed');
 await browser.close();console.log('PASS Grade 10 A-F (45 objective+2 writing), corrected four-unit reading, mixed audio provenance, random and untimed skills');
})().catch(e=>{console.error(e);process.exit(1)});
