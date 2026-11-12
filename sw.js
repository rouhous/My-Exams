const CACHE='my-exams-v3-2026-11-12';
const CORE=['./','index.html','review.html','tasks_5_to_9_corrected.json','higher_grades_corrected.json','curriculum_units.json','OFFLINE_MEDIA_MANIFEST.json'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil((async()=>{for(const n of await caches.keys())if(n.startsWith('exam-static-')||n.startsWith('my-exams-')&&n!==CACHE)await caches.delete(n);await self.clients.claim()})()));
self.addEventListener('fetch',e=>{const req=e.request;if(req.method!=='GET'||new URL(req.url).origin!==location.origin)return;
e.respondWith((async()=>{const c=await caches.open(CACHE);if(req.mode==='navigate'){try{const r=await fetch(req);if(r.ok)c.put(req,r.clone());return r}catch(err){return await c.match(req)||await c.match('index.html')||Response.error()}}
const old=await c.match(req,{ignoreSearch:true});if(old)return old;try{const r=await fetch(req);if(r.ok&&r.type!=='opaque')c.put(req,r.clone());return r}catch(err){return old||Response.error()}})())});
