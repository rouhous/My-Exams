const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:390,height:850}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765/listening-media-review.html',{waitUntil:'domcontentloaded'});
 for(const g of [5,6,7,8,9]){
  await page.selectOption('#grade',String(g));
  await page.waitForFunction(x=>document.querySelector('#status').textContent.includes('الصف '+x+':'),g,{timeout:30000});
  const count=await page.locator('.pic img').count();
  const expected=g===9?105:(g===5||g===6?120:60);
  if(count!==expected)throw Error('Grade '+g+' pictures '+count+' != '+expected);
  await page.waitForFunction(()=>[...document.querySelectorAll('.pic img')].every(im=>im.complete),null,{timeout:20000});
  const bad=await page.locator('.pic img').evaluateAll(images=>images.filter(im=>!im.naturalWidth).map(im=>im.src));
  if(bad.length)throw Error('Grade '+g+' broken: '+bad.join(', '));
  const questions=await page.locator('.q').count();
  if(questions!==(g===9?35:20))throw Error('Grade '+g+' question count '+questions);
  if(await page.locator('.pic.good img').count()!==questions)throw Error('Grade '+g+' correct answer picture mapping');
 }
 if(errors.length)throw Error(errors.join('; '));
 await browser.close();
 console.log('PASS grade 5-9 illustrated listening: 465 image loads, 115 items, answer-to-picture maps');
})().catch(err=>{console.error(err);process.exit(1)});
