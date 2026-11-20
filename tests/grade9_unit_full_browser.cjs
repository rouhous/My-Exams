const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:390,height:844}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765/grade9/unit-exams/index.html',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>!document.querySelector('#start').disabled,{timeout:30000});
 for(const unit of ['U1','U2','U3']){
  await page.selectOption('#unit',unit);
  await page.click('#start');
  if(await page.locator('.section').count()!==7)throw Error(unit+' seven tasks missing');
  if(await page.locator('.q').count()!==30)throw Error(unit+' 30 questions missing');
  if(await page.locator('.images img').count()!==15)throw Error(unit+' listening pictures missing');
  if(await page.locator('audio').count()!==2)throw Error(unit+' two MP3 missing');
  const numberedTrack=await page.locator('audio').first().getAttribute('src');
  if(!numberedTrack?.endsWith('-listening-1-two-pass.mp3'))throw Error(unit+' numbered two-pass track missing');
  if(!(await page.locator('#clock').textContent()).startsWith('02:'))throw Error(unit+' 120min timer missing');
  await page.click('#end');
  if(!(await page.locator('#results').textContent()).includes('0 / 30'))throw Error(unit+' objective count wrong');
  if(!(await page.locator('#results').textContent()).includes('30 blank'))throw Error(unit+' short answer count wrong');
  await page.click('#back');
 }
 await page.selectOption('#mode','skill');await page.selectOption('#skill','2');await page.click('#start');
 if(await page.locator('.section').count()!==1||await page.locator('.q').count()!==10)throw Error('untimed grammar cloze incomplete');
 if(!(await page.locator('#clock').isHidden()))throw Error('untimed skill clock visible');
 if(errors.length)throw Error('JS errors '+errors.join(' | '));
 console.log('PASS three original Grade9 unit papers, 30 questions each, 15 pictures, 2 MP3, 120min, isolated skill.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
