const { chromium, devices } = require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:420,height:860},serviceWorkers:'allow'});
 const page=await context.newPage();
 page.on('pageerror',e=>{console.log('PAGE ERROR',e.message)});
 const base='http://127.0.0.1:8765/';
 async function g56(grade){
   await context.setOffline(false);
   await page.goto(base+'grades5-6/index.html',{waitUntil:'domcontentloaded'});
   await page.selectOption('#grade',String(grade));
   await page.selectOption('#model','E');
   await page.click('#startExam');
   let n=await page.locator('#session section.section').count();
   if(n!==8)throw Error('Grade '+grade+' mixed E had '+n+' sections, expected 8');
   const audios=await page.locator('#session audio').count();
   if(audios!==2)throw Error('Grade '+grade+' mixed E had '+audios+' audio players');
   await page.click('#back');
   await page.selectOption('#model','F');
   await page.click('#startExam');
   n=await page.locator('#session section.section').count();
   if(n!==8)throw Error('Grade '+grade+' mixed F had '+n+' sections');
   await page.click('#back');
   for(let attempt=0;attempt<6;attempt++){
     await page.click('#randomExam');
     n=await page.locator('#session section.section').count();
     if(n!==8)throw Error('Grade '+grade+' random test had '+n+' sections');
     const samples=await page.evaluate(()=>state.acts.map(x=>x.sourceModel));
     const counts=Object.fromEntries(['A','B','C','D'].map(x=>[x,samples.filter(y=>y===x).length]));
     if(Object.values(counts).some(x=>x!==2))throw Error('Grade '+grade+' random models not balanced '+JSON.stringify(counts));
     const audioCount=await page.locator('#session audio').count();
     if(audioCount!==2)throw Error('Grade '+grade+' random lacks exactly two audios');
     await page.click('#back');
   }
   console.log('PASS grades5-6',grade,'both mixed papers, six balanced randomized papers');
 }
 async function g78(grade){
   await context.setOffline(false);
   await page.goto(base+'grades7-8/index.html',{waitUntil:'domcontentloaded'});
   await page.selectOption('#grade',String(grade));
   await page.selectOption('#model','E');
   await page.click('#start');
   let n=await page.locator('.section-title').count();
   if(n!==7)throw Error('Grade '+grade+' mixed E had '+n+' sections');
   let imgs=await page.locator('img[src^="assets/illustrations/"]').count();
   if(imgs!==15)throw Error('Grade '+grade+' listening pictures '+imgs+', expected 15');
   await page.selectOption('#model','F');
   await page.click('#start');
   n=await page.locator('.section-title').count();
   if(n!==7)throw Error('Grade '+grade+' mixed F had '+n+' sections');
   await page.click('#randomNew');
   n=await page.locator('.section-title').count();
   if(n!==7)throw Error('Grade '+grade+' random R had '+n+' sections');
   for(let attempt=0;attempt<6;attempt++){
     await page.click('#randomNew');
     n=await page.locator('.section-title').count();
     if(n!==7)throw Error('Grade '+grade+' randomized paper has '+n+' sections');
     const models=await page.evaluate(()=>current.sections.map(x=>x.sourceModel));
     const counts=Object.fromEntries(['A','B','C','D'].map(x=>[x,models.filter(y=>y===x).length]));
     if(Object.values(counts).some(x=>x<1||x>2))throw Error('Grade '+grade+' random models unbalanced '+JSON.stringify(counts));
     const imgs=await page.locator('img[src^="assets/illustrations/"]').count();
     if(imgs!==15)throw Error('Grade '+grade+' randomized listening missing illustrations');
   }
   console.log('PASS grades7-8',grade,'E/F plus six balanced randomized papers with 15 listening pictures');
 }
 await g56(5);
 await g56(6);
 await g78(7);
 await g78(8);
 await context.setOffline(false);
 await page.goto(base+'grades5-6/index.html',{waitUntil:'domcontentloaded'});
 await page.selectOption('#grade','5');
 await page.selectOption('#model','E');
 await page.click('#packDownload');
 await page.waitForFunction(()=>document.querySelector('#packProgress').textContent.includes('اكتمل التنزيل'),null,{timeout:120000});
 const m=await page.locator('#packProgress').textContent();
 console.log('Offline cache progress',m);
 await context.setOffline(true);
 await page.reload({waitUntil:'domcontentloaded'});
 await page.selectOption('#grade','5');
 await page.selectOption('#model','E');
 await page.click('#startExam');
 const count=await page.locator('#session section.section').count();
 if(count!==8)throw Error('Offline Grade 5 mixed exam did not render');
 const a=page.locator('#session audio').first();
 const url=await a.getAttribute('src');
 const result=await page.evaluate(async src=>{
   const response=await fetch(src,{headers:{range:'bytes=0-1023'}});
   return {status:response.status,size:(await response.arrayBuffer()).byteLength,type:response.headers.get('content-type')};
 },url);
 if(![200,206].includes(result.status)||result.size<100)throw Error('Offline MP3 range fetch failed '+JSON.stringify(result));
 console.log('PASS offline grade 5 E with MP3',result);
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
