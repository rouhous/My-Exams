/* My Exams offline router v4. Supports MP3 range requests and previous exam media caches. */
const SHELL_CACHE='my-exams-shell-v36', MEDIA_CACHE='my-exams-media-v5';
const SAVED_PAPERS='my-exams-downloaded-papers-v1';
const SHELL=['shared/journey-results.js','shared/exam-pages.js','shared/exam-pages.css','shared/mixed-exam-links.js','mixed-exams/index.html','mixed-exams/assemble.js','mixed-exams/paper.js','mixed-exams/paper.css','./','index.html','exams.html','grade-skills.html','grade12-skills.html','shared/grade-catalogue.js','shared/oman-theme.css','shared/assessment-theme.css','shared/oman-hero.svg','shared/oman-hero.webp','grade9/index.html','grade9/data.js','grade9/natural_audio.js','grade9/natural_player.js','grades5-6/index.html','grades7-8/index.html','shared/exam-tools.js','shared/exam-tools.css','shared/reading-split.css','shared/reading-split.js','shared/short-answer-marking.js','shared/data-charts.js','shared/learning-feedback.js','grade10/index.html','grade10/data.json','review.html','grade12/core/units/index.html','grade11/core/units/paper-a-preview.html','grade11/core/units/unit1-paper-a.json','grade11/core/units/unit1-listening1-original-draft.json','grade11/core/units/unit1-listening2-original-draft.json','grade11/core/units/paper-c-preview.html','grade11/core/units/unit3-paper-c.json','grade11/core/units/unit3-listening1-original-draft.json','grade11/core/units/unit3-listening2-original-draft.json','grade11/core/units/paper-d-preview.html','grade11/core/units/unit4-paper-d.json','grade11/core/units/unit4-listening1-original-draft.json','grade11/core/units/unit4-listening2-original-draft.json','grade12/core/units/paper-c-preview.html','grade12/core/units/unit3-paper-c.json','grade12/core/units/unit3-listening1-original-draft.json','grade12/core/units/unit3-listening2-original-draft.json','grade12/core/units/paper-d-preview.html','grade12/core/units/unit4-paper-d.json','grade12/core/units/unit4-listening1-original-draft.json','grade12/core/units/unit4-listening2-original-draft.json','grade12/core/units/paper-a-preview.html','grade12/core/units/paper-b-preview.html','grade12/core/units/unit2-paper-b.json','grade12/core/units/unit2-listening1-original-draft.json','grade12/core/units/unit2-listening2-original-draft.json','grade12/core/units/unit2-reading2-original-draft.json','grade12/core/units/unit2-reading3-original-draft.json','grade12/core/units/unit2-supporting-sections.json','grade12/core/units/unit1-paper-a.json','grade12/core/units/unit1-listening1-original-draft.json','grade12/core/units/unit1-listening2-original-draft.json','grade11/core/units/paper-b-preview.html','grade11/core/units/unit2-paper-b.json','grade11/core/units/unit2-listening1-original-draft.json','grade11/core/units/unit2-listening2-original-draft.json','grade11/elective/units/index.html','grade11/elective/units/paper-a-preview.html','grade11/elective/units/paper-c-preview.html','grade11/elective/units/unit3-listening1-original-draft.json','grade11/elective/units/unit3-listening2-original-draft.json','grade11/elective/units/unit3-reading1-original-draft.json','grade11/elective/units/unit3-reading2-original-draft.json','grade11/elective/units/unit3-writing-original-draft.json','grade11/elective/units/paper-d-preview.html','grade11/elective/units/unit4-listening1-original-draft.json','grade11/elective/units/unit4-listening2-original-draft.json','grade11/elective/units/unit4-reading1-original-draft.json','grade11/elective/units/unit4-reading2-original-draft.json','grade11/elective/units/unit4-writing-original-draft.json','grade11/elective/units/paper-b-preview.html','grade11/elective/units/unit2-listening1-original-draft.json','grade11/elective/units/unit2-listening2-original-draft.json','grade11/elective/units/unit2-reading1-original-draft.json','grade11/elective/units/unit2-reading2-original-draft.json','grade11/elective/units/unit2-writing-original-draft.json','grade11/elective/units/unit1-reading1-original-draft.json','grade11/elective/units/unit1-reading2-original-draft.json','grade11/elective/units/unit1-writing-original-draft.json','grade11/elective/units/unit1-listening1-original-draft.json','grade11/elective/units/unit1-listening2-original-draft.json','targeted_units/index.html','targeted_units/full_papers.json','grade9/unit-exams/index.html','grade9/unit-exams/models.json','grade9/unit-exams/audio/manifest.json','grade9/unit-remediation/index.html','grade9/unit-remediation/units.json','tasks_5_to_9_corrected.json','higher_grades_corrected.json','upper-grades-practice.html','grade12/elective/units/index.html','grade12/elective/units/unit1-listening1-original-draft.json','grade12/elective/units/unit1-listening2-original-draft.json','grade12/elective/units/paper-a-preview.html','grade12/elective/units/unit1-reading1-original-draft.json','grade12/elective/units/unit1-reading2-original-draft.json','grade12/elective/units/unit1-writing-original-draft.json','grade12/elective/index.html','exam-inventory.html','final-inventory.html','FINAL_RELEASE_AUDIT_2026-11-14.json','listening-media-review.html','EXAM_INVENTORY_2026-11-14.json','MEDIA_STATUS_2026-11-14.json','GRADE9_LISTENING_IMAGE_VISUAL_REVIEW_2026-11-14.json','grade12/elective/units/unit2-listening1-original-draft.json','grade12/elective/units/unit2-listening2-original-draft.json','grade12/elective/units/unit2-reading1-original-draft.json','grade12/elective/units/unit2-reading2-original-draft.json','grade12/elective/units/unit2-writing-original-draft.json','grade12/elective/units/unit3-listening1-original-draft.json','grade12/elective/units/unit3-listening2-original-draft.json','grade12/elective/units/unit3-reading1-original-draft.json','grade12/elective/units/unit3-reading2-original-draft.json','grade12/elective/units/unit3-writing-original-draft.json','grade12/elective/units/unit4-listening1-original-draft.json','grade12/elective/units/unit4-listening2-original-draft.json','grade12/elective/units/unit4-reading1-original-draft.json','grade12/elective/units/unit4-reading2-original-draft.json','grade12/elective/units/unit4-writing-original-draft.json','curriculum_units.json','OFFLINE_MEDIA_MANIFEST.json'];
self.addEventListener('install',e=>e.waitUntil((async()=>{const cache=await caches.open(SHELL_CACHE);await Promise.allSettled(SHELL.map(async path=>{const response=await fetch(path,{cache:'no-store'});if(response.ok)await cache.put(path,response)}));await self.skipWaiting()})()));
self.addEventListener('activate',e=>e.waitUntil((async()=>{for(const key of await caches.keys()){if(key.startsWith('my-exams-shell-v')&&key!==SHELL_CACHE)await caches.delete(key)}await self.clients.claim()})()));
/* Prefer the current shell. Older caches can hold outdated CSS/JS that destroyed the mobile layout. */
async function fromCache(req,legacyMedia=false){
  const names=[SHELL_CACHE,MEDIA_CACHE,SAVED_PAPERS];
  if(legacyMedia){for(const key of (await caches.keys()).reverse())if(!names.includes(key))names.push(key)}
  for(const name of names){const hit=await (await caches.open(name)).match(req,{ignoreSearch:true});if(hit)return hit}
  return null;
}
async function rangeResponse(req,res){
  const range=req.headers.get('range');
  if(!range||!res||!res.ok||res.status===206)return res;
  const mime=res.headers.get('content-type')||'';
  if(!mime.includes('audio/')&&!/\.(mp3|wav|m4a|ogg)$/i.test(new URL(req.url).pathname))return res;
  const buf=await res.arrayBuffer(),total=buf.byteLength;
  const m=/^bytes=(\d*)-(\d*)$/.exec(range);
  if(!m)return new Response(null,{status:416,headers:{'Content-Range':`bytes */${total}`}});
  let start=m[1]?Number(m[1]):0,end=m[2]?Number(m[2]):total-1;
  if(!m[1]&&m[2]){start=Math.max(0,total-end);end=total-1}
  if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start>=total||start>end)return new Response(null,{status:416,headers:{'Content-Range':`bytes */${total}`}});
  end=Math.min(end,total-1);
  return new Response(buf.slice(start,end+1),{status:206,headers:{
    'Content-Type':mime||'audio/mpeg','Content-Range':`bytes ${start}-${end}/${total}`,
    'Accept-Ranges':'bytes','Content-Length':String(end-start+1)
  }});
}
self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET'||new URL(req.url).origin!==self.location.origin)return;
  event.respondWith((async()=>{
    if(req.mode==='navigate'){
      try{const net=await fetch(req);if(net.ok)await (await caches.open(SHELL_CACHE)).put(req,net.clone());return net}
      catch(e){return await fromCache(req)||await fromCache(new URL('index.html',self.registration.scope).href)||Response.error()}
    }
    const path=new URL(req.url).pathname;
    const sourceFile=/\.(?:css|js|json)$/i.test(path);
    /* Network-first CSS/JS/JSON prevents old exam banks and charts from persisting after updates. */
    if(sourceFile){
      try{
        const live=await fetch(req,{cache:'no-store'});
        if(live.ok){await (await caches.open(SHELL_CACHE)).put(req,live.clone());return live}
      }catch(e){}
      return await fromCache(req)||Response.error();
    }
    const media=/\.(?:mp3|wav|m4a|ogg|png|jpe?g|webp|svg)$/i.test(path);
    const cached=await fromCache(req,media);
    if(cached)return req.headers.has('range')?rangeResponse(req,cached):cached;
    try{
      const net=await fetch(req);
      if(net.ok&&net.status===200&&net.type!=='opaque'&&!req.headers.has('range'))
        await (await caches.open(MEDIA_CACHE)).put(req,net.clone());
      return net;
    }catch(e){return Response.error()}
  })());
});