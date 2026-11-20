const { chromium, devices } = require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:420,height:860},serviceWorkers:'allow'});
 const page=await context.newPage();
 page.on('pageerror',e=>{console.log('PAGE ERROR',e.message)});
 const base='http://127.0.0.1:8765/';
 async function mixed(grade, mode) {
   const path = grade <= 6 ? 'grades5-6/index.html' : 'grades7-8/index.html';
   const model = grade === 5 ? 'E' : 'D';
   await page.goto(base + path + '?grade=' + grade + '&model=' + model + '&mode=' + mode,{waitUntil:'commit'});
   await page.waitForURL('**/mixed-exams/index.html?**');
   await page.locator('#finish').waitFor({state:'visible'});
   const result = await page.evaluate(() => ({
     sections: document.querySelectorAll('#paper .exam-part').length,
     all: [...document.querySelectorAll('#paper .exam-part')].map(section => (
       [...section.querySelectorAll('[data-unit]')].map(item => item.dataset.unit)
     )),
     writing: [...document.querySelectorAll('.writing-task')].map(item => item.dataset.unit)
   }));
   if (result.sections !== 8) throw Error('Unexpected section count for grade ' + grade);
   const expected = grade === 5 ? 4 : 3;
   if (result.all.slice(0,-2).some(items => new Set(items).size !== expected))
     throw Error('Missing unit in a mixed section for grade ' + grade);
   if (new Set(result.writing).size !== 2) throw Error('Writing tasks repeated a unit');
   if (grade >= 7 && await page.locator('#listening1 img').count() !== 15)
     throw Error('Missing listening pictures for grade ' + grade);
   const signature = await page.locator('#paper .question h3').allTextContents();
   if (mode === 'random') {
     await page.locator('#newPaper').click();
     await page.locator('#finish').waitFor({state:'visible'});
     if (JSON.stringify(signature) === JSON.stringify(await page.locator('#paper .question h3').allTextContents()))
       throw Error('Random paper did not change for grade ' + grade);
   }
   console.log('PASS mixed content and legacy route',grade,mode);
 }
 for (const grade of [5,6,7,8]) {
   await mixed(grade,'exam');
   await mixed(grade,'random');
 }
 await page.goto(base+'mixed-exams/index.html?grade=5&mode=exam');
 await page.locator('#offline summary, .offline summary').click();
 await page.locator('#download').click();
 await page.getByText('This paper is ready for offline use on this device.').waitFor({timeout:120000});
 await context.setOffline(true);
 await page.reload({waitUntil:'domcontentloaded'});
 await page.locator('#listening1-prepare').click();
 await page.getByText('Recording ready. Press play to begin.').waitFor({timeout:45000});
 const audio = page.locator('#listening1 audio');
 await audio.waitFor({state:'visible'});
 if(!(await audio.getAttribute('src')).startsWith('blob:')) throw Error('Mixed offline recording missing');
 console.log('PASS mixed Grade 5 paper and assembled offline recording');
 await context.setOffline(false);
 await page.goto(base+'grades5-6/index.html',{waitUntil:'domcontentloaded'});
 await page.selectOption('#grade','5');
 await page.selectOption('#model','C');
 await page.click('#packDownload');
 await page.waitForFunction(()=>document.querySelector('#packProgress').textContent.includes('اكتمل التنزيل'),null,{timeout:120000});
 await context.setOffline(true);
 await page.reload({waitUntil:'domcontentloaded'});
 await page.selectOption('#grade','5');
 await page.selectOption('#model','C');
 await page.click('#startExam');
 if(await page.locator('#session section.section').count()!==8)throw Error('Grade 5 space unit not available offline');
 const spaceResources=await page.evaluate(async()=>{
  const endpoints=['images/rocket.webp','images/telescope.webp','images/planet.webp','images/spacesuit.webp','images/moon.webp','audio-reviewed/g5-c-listening-1.mp3'];
  return await Promise.all(endpoints.map(async file=>{
   const r=await fetch(file,file.endsWith('.mp3')?{headers:{range:'bytes=0-1023'}}:{});
   return {file,status:r.status,bytes:(await r.arrayBuffer()).byteLength};
  }));
 });
 if(spaceResources.some(x=>![200,206].includes(x.status)||x.bytes<100))throw Error('Missing offline space-unit resource '+JSON.stringify(spaceResources));
 console.log('PASS Grade 5 space-unit illustrations and natural MP3 offline',spaceResources);
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
