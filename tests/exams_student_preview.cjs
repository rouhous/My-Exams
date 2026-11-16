const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const base='http://127.0.0.1:8765',errors=[];
 const page=await browser.newPage({viewport:{width:390,height:844}});
 page.on('pageerror',error=>errors.push(error.message));
 await page.goto(base+'/exams/index.html',{waitUntil:'domcontentloaded'});
 if(await page.locator('.tile').count()!==8)throw Error('Exams hub must expose exactly eight student grade links');
 for(let grade=5;grade<=12;grade++){
  await page.goto(base+'/exams/grade-'+grade+'/index.html',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>{const el=document.querySelector('iframe');return !!el&&!!el.contentDocument?.body?.textContent?.trim()},{timeout:30000});
  const frame=page.frameLocator('iframe');
  if(grade<=8){
    await frame.locator('#grade').waitFor({timeout:12000});
    const actual=await frame.locator('#grade').inputValue();
    if(actual!==String(grade))throw Error('Grade '+grade+' wrong grade '+actual);
    if(await frame.locator('#grade').isEnabled())throw Error('Grade '+grade+' must be locked in student link');
  }
  if(grade===9){
    await frame.locator('#unit').waitFor({timeout:12000});
    if(await frame.locator('#unit option').count()!==3)throw Error('Grade 9 requires three distinct unit exams');
  }
  if(grade===11||grade===12){
    if(await page.locator('#course option').count()!==2)throw Error('Core + elective missing for '+grade);
    if(await page.locator('#unit option').count()!==4)throw Error('Four unit links missing for '+grade);
    await page.selectOption('#course','elective');
    await page.selectOption('#unit','d');
    await page.waitForTimeout(300);
    const src=await page.locator('iframe').getAttribute('src');
    if(!src.includes('grade'+grade+'/elective/units/paper-d-preview.html'))throw Error('Wrong elective/Unit 4 path '+src);
  }
  console.log('PASS independent student URL, Grade '+grade);
 }
 if(errors.length)throw Error('Page runtime errors: '+errors.join(' | '));
 await browser.close();
 console.log('PASS all eight Grades 5-12 student routes and separate grade locks');
})().catch(e=>{console.error(e);process.exit(1)});
