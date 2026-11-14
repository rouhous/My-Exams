const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:400,height:820}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765/upper-grades-practice.html',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.querySelector('#loadState').textContent.includes('Review bank loaded'),null,{timeout:30000});
 const cases=[['11-elective',6,40,150,60],['12-core',9,50,180,70],['12-elective',6,45,180,70]];
 for(const [track,sections,items,mins,marks] of cases){
   await page.selectOption('#track',track);
   await page.selectOption('#mode','full');
   for(const id of 'ABCD'){
     await page.selectOption('#model',id);await page.click('#start');
     const n=await page.locator('#questions section.part').count(),q=await page.locator('#questions .question').count();
     if(n!==sections||q!==items)throw Error(track+' '+id+': sections '+n+'/'+sections+', questions '+q+'/'+items);
     const tm=await page.locator('#timer').textContent();
     if(!tm.includes('Time left '+mins+':')&&!tm.includes('Time left '+(mins-1)+':'))throw Error(track+' '+id+' wrong timer '+tm);
     if(!(await page.locator('#paperMeta').textContent()).includes(String(marks)+' total paper marks'))throw Error(track+' wrong marks');
     await page.click('#reset');
   }
   await page.selectOption('#mode','random');await page.click('#start');
   if(await page.locator('#questions section.part').count()!==sections)throw Error(track+' random missing sections');
   if(await page.locator('#questions .question').count()!==items)throw Error(track+' random wrong question count');
   const s=await page.locator('#questions section.part .meta').allTextContents();
   if(s.some(t=>!/Source model [A-D]/.test(t)))throw Error(track+' random not from fixed A-D: '+s.join(','));
   await page.click('#reset');
   await page.selectOption('#mode','skill');await page.selectOption('#skill','rdg2');await page.click('#start');
   if(await page.locator('#questions section.part').count()!==1)throw Error(track+' skill should be single section');
   if((await page.locator('#timer').textContent())!=='No time limit')throw Error(track+' skill incorrectly timed');
   await page.click('#submit');
   if(!(await page.locator('#result').textContent()).includes('automatically scored option questions'))throw Error(track+' missing honest score message');
   await page.click('#reset');
 }

 await page.goto('http://127.0.0.1:8765/grade12/elective/units/index.html',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.querySelectorAll('#quiz .q').length===10,null,{timeout:30000});
 if(await page.locator('#quiz .q').count()!==10)throw Error('The Arts listening draft question count is not ten');
 const source=await page.evaluate(async()=>{
    const r=await fetch('unit1-listening1-original-draft.json');
    const d=await r.json();
    d.questions.forEach((q,i)=>{
      const input=document.querySelector('input[name="q'+i+'"][value="'+q.answer+'"]');
      if(!input)throw Error('Missing correct option '+i);
      input.checked=true;
    });
    return {words:d.wordCount,turns:d.speakerTurns,mc:d.questions.filter(q=>q.type==='mc').length,tf:d.questions.filter(q=>q.type==='tf').length};
 });
 if(source.words<400||source.words>450||source.turns<25||source.turns>30||source.mc!==6||source.tf!==4)throw Error('The Arts listening format mismatch '+JSON.stringify(source));
 await page.click('#mark');
 if(!(await page.locator('#feedback').textContent()).includes('10 / 10 correct'))throw Error('The Arts answer checking failed');

 if(errors.length)throw Error('Browser errors: '+errors.join('; '));
 await browser.close();console.log('PASS upper grade A-D, timed full, randomized complete, independent untimed skill and honest score review');
})().catch(e=>{console.error(e);process.exit(1)});
