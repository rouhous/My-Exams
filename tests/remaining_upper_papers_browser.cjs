const { chromium }=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:390,height:844}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765/targeted_units/index.html',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.querySelector('#paperSelect').options.length===8,{timeout:30000});
 const ids=await page.locator('#paperSelect option').evaluateAll(a=>a.map(o=>o.value));
 if(new Set(ids).size!==8)throw Error('Eight unique papers required');
 for(const id of ids){
   await page.selectOption('#paperSelect',id);
   await page.selectOption('#mode','skill');
   await page.selectOption('#skill','rdg2');
   await page.waitForFunction(()=>!document.querySelector('#start').disabled);
   await page.click('#start');
   if(await page.locator('section.part').count()!==1)throw Error(id+' skill isolation failed');
   if(!(await page.locator('#clock').isHidden()))throw Error(id+' skill should have no clock');
   await page.click('#finish');
   if(!(await page.locator('#results').textContent()).includes('teacher review'))throw Error(id+' answer review missing');
   await page.click('#back');
   await page.selectOption('#mode','full');
   const ready=(await page.locator('#status').textContent()).includes('MP3: 2/2');
   if(ready){
     if(await page.locator('#start').isDisabled())throw Error(id+' all sources verified but paper locked');
     await page.click('#start');
     const expected=id.includes('elective')?6:9;
     if(await page.locator('section.part').count()!==expected)throw Error(id+' full section mismatch');
     if(await page.locator('audio').count()!==2)throw Error(id+' missing source-verified MP3');
     const marks=id.startsWith('12-')?70:60;
     if(!(await page.locator('#paperMarks').textContent()).includes(marks+' marks'))throw Error(id+' marks invalid');
     await page.click('#finish');await page.click('#back');
   }else if(!(await page.locator('#start').isDisabled()))throw Error(id+' full paper unlocked without MP3');
 }
 if(errors.length)throw Error('Browser page errors: '+errors.join(' | '));
 console.log('PASS 8 original unit papers, isolated skills, locked-until-sound full papers, auto/manual review.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
