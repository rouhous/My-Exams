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

 await page.selectOption('#task','2');
 await page.waitForFunction(()=>document.querySelectorAll('#quiz .q').length===10&&document.querySelector('#taskTitle').textContent.includes('Listening 2'),null,{timeout:30000});
 const second=await page.evaluate(async()=>{
  const r=await fetch('unit1-listening2-original-draft.json');const d=await r.json();
  return {words:d.wordCount,actualWords:d.script.trim().split(/\s+/).length,notes:d.questions.filter(q=>q.type==='note').length,short:d.questions.filter(q=>q.type==='short').length,blankOptions:d.questions.every(q=>!q.options)};
 });
 if(second.words<450||second.words>500||second.actualWords!==second.words||second.notes!==5||second.short!==5||!second.blankOptions)throw Error('Listening 2 shape mismatch '+JSON.stringify(second));
 await page.locator('input[name="q0"]').fill('school auditorium');
 await page.click('#mark');
 if(!(await page.locator('#feedback').textContent()).includes('Teacher review required'))throw Error('Listening 2 must not receive unreliable automatic score');


 await page.goto('http://127.0.0.1:8765/grade12/elective/units/paper-a-preview.html',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>document.querySelector('#start')&&!document.querySelector('#start').disabled,null,{timeout:30000});
 await page.click('#start');
 if(await page.locator('#sections section.part').count()!==6)throw Error('The Arts complete model is missing sections');
 if(await page.locator('#sections .question').count()!==45)throw Error('The Arts model must include 45 objective/short questions');
 if(await page.locator('#sections textarea').count()!==2)throw Error('The Arts model must include both writing tasks');
 const clock=await page.locator('#clock').textContent();
 if(!clock.includes('Time left 180:')&&!clock.includes('Time left 179:'))throw Error('The Arts complete model must have 180-minute clock');
 if(!(await page.locator('#paperMarks').textContent()).includes('70 marks'))throw Error('The Arts marks mismatch');
 await page.click('#finish');
 const fullReview=await page.locator('#results').textContent();
 if(!fullReview.includes('0 / 23')||!fullReview.includes('22 notes or short answers'))throw Error('The Arts full marking must separate 23 auto vs 22 manual items: '+fullReview.slice(0,400));
 await page.click('#restart');
 await page.selectOption('#mode','skill');
 await page.selectOption('#skill','rdg1');
 await page.click('#start');
 if(await page.locator('#sections section.part').count()!==1)throw Error('The Arts independent reading should be single section');
 if((await page.locator('#clock').textContent())!=='Untimed')throw Error('The Arts single skill must be untimed');
 if(await page.locator('#sections .question').count()!==12)throw Error('The Arts reading 1 should have twelve questions');
 await page.click('#restart');

 if(errors.length)throw Error('Browser errors: '+errors.join('; '));
 await browser.close();console.log('PASS upper grade A-D, timed full, randomized complete, independent untimed skill and honest score review');
})().catch(e=>{console.error(e);process.exit(1)});
