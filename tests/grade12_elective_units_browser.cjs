const {chromium}=require('playwright');
(async()=>{
  const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:390,height:844}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(let u=1;u<=4;u++){
    await page.goto('http://127.0.0.1:8765/grade12/elective/units/paper-a-preview.html?unit='+u,{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>!document.getElementById('start').disabled,{timeout:30000});
    await page.click('#start');
    if(await page.locator('#sections section.part').count()!==6)throw Error('Unit '+u+' missing one of six sections');
    const questions=await page.locator('#sections .question').count();
    if(questions!==45)throw Error('Unit '+u+' question count is '+questions+' not 45');
    if(await page.locator('#sections textarea').count()!==2)throw Error('Unit '+u+' missing writing 1/2');
    if(!(await page.locator('#paperMarks').textContent()).includes('70 marks'))throw Error('Unit '+u+' not 70 marks');
    if(!(await page.locator('#clock').textContent()).includes('Time left 180:')&&!(await page.locator('#clock').textContent()).includes('Time left 179:'))throw Error('Unit '+u+' 180 min timer missing');
    const sections=await page.locator('#sections section.part h2').allTextContents();
    if(!sections[0].includes('Listening 1')||!sections.at(-1).includes('Writing 2'))throw Error('Incorrect section order Unit '+u);
    await page.click('#finish');
    if(!(await page.locator('#results').textContent()).includes('0 / 23'))throw Error('Unit '+u+' automated objective split not 23');
    if(!(await page.locator('#results').textContent()).includes('22 notes or short answers'))throw Error('Unit '+u+' manual items not 22');
    await page.click('#restart');
    await page.selectOption('#mode','skill');
    await page.selectOption('#skill','rdg2');
    await page.click('#start');
    if(await page.locator('#sections section.part').count()!==1)throw Error('Unit '+u+' skill mode not isolated');
    if(await page.locator('#sections .question').count()!==13)throw Error('Unit '+u+' reading 2 not 13 questions');
    if((await page.locator('#clock').textContent())!=='Untimed')throw Error('Unit '+u+' isolated skill not untimed');
  }
  await page.goto('http://127.0.0.1:8765/grade12/elective/units/paper-a-preview.html?mixed=1');
  await page.waitForFunction(()=>document.querySelector('#start')&&!document.querySelector('#start').disabled,null,{timeout:30000});
  await page.click('#start');
  if(await page.locator('#sections section.part').count()!==6)throw Error('Comprehensive random must have six complete tasks');
  if(await page.locator('#sections .question').count()!==45)throw Error('Comprehensive random must have exactly 45 objective or short items');
  if(await page.locator('#sections textarea').count()!==2)throw Error('Comprehensive random missing two writing prompts');
  if(!(await page.locator('#paperMarks').textContent()).includes('70 marks'))throw Error('Comprehensive random must total 70 marks');
  const sourceLabels=await page.locator('#sections .part > p.meta').allTextContents();
  const from=new Set(sourceLabels.map(t=>{const m=t.match(/Source unit (\d)/);return m?.[1]}));
  if(from.size!==4)throw Error('Comprehensive random must draw from four source units, instead got '+JSON.stringify(sourceLabels));
  if(!sourceLabels.every(t=>/Source unit [1-4]:/.test(t)))throw Error('Missing provenance in comprehensive random');
  await page.click('#restart');
  await page.waitForFunction(()=>document.querySelector('#start')&&!document.querySelector('#start').disabled,null,{timeout:30000});

  await page.goto('http://127.0.0.1:8765/grade12/elective/index.html');
  if(await page.locator('.unit').count()!==4)throw Error('Missing Grade 12 elective 4-unit menu');
  if(errors.length)throw Error('Browser script errors: '+errors.join('; '));
  await browser.close();
  console.log('PASS: four G12 elective fixed unit papers A with 6 sections, 70 marks, 180-minute complete, untimed isolated skills, accurate objective vs manual marking');
})().catch(e=>{console.error(e);process.exit(1)});
