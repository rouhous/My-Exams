/* My Exams offline router v4. Supports MP3 range requests and previous exam media caches. */
const SHELL_CACHE='my-exams-shell-v5', MEDIA_CACHE='my-exams-media-v4';
const SHELL=['./','index.html','review.html','tasks_5_to_9_corrected.json','higher_grades_corrected.json','upper-grades-practice.html','curriculum_units.json','OFFLINE_MEDIA_MANIFEST.json'];
self.addEventListener('install',e=>e.waitUntil((async()=>{await (await caches.open(SHELL_CACHE)).addAll(SHELL);await self.skipWaiting()})()));
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
async function fromCache(req){
  for(const name of await caches.keys()){
    const hit=await (await caches.open(name)).match(req,{ignoreSearch:true});
    if(hit)return hit;
  }
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
    const cached=await fromCache(req);
    if(cached)return req.headers.has('range')?rangeResponse(req,cached):cached;
    try{
      const net=await fetch(req);
      if(net.ok&&net.status===200&&net.type!=='opaque'&&!req.headers.has('range'))
        await (await caches.open(MEDIA_CACHE)).put(req,net.clone());
      return net;
    }catch(e){return Response.error()}
  })());
});