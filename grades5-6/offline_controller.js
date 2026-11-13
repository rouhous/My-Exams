/* Shared Grade 5–9 offline pack: verify complete local files before reporting success. */
(()=>{
const VERSION='my-exams-media-v4';
async function register(){
 if(!('serviceWorker' in navigator)||location.protocol==='file:')return false;
 try{const root=new URL('../sw.js',location.href);await navigator.serviceWorker.register(root.href,{scope:new URL('../',location.href).pathname});await navigator.serviceWorker.ready;return true}
 catch(e){console.warn('Offline worker unavailable',e);return false}
}
async function saveAll(files,report){
 if(location.protocol==='file:')return {ok:false,reason:'افتح التطبيق على GitHub Pages عبر HTTPS لتنزيل ملفات العمل دون إنترنت والتحقق منها.'};
 if(!(await register())||!('caches' in window))return {ok:false,reason:'Offline storage unavailable in this browser'};
 const cache=await caches.open(VERSION),unique=[...new Set(files.map(String))],failed=[];let progress=0;
 for(const name of unique){
  try{
   const url=new URL(name,location.href);
   if(url.origin!==location.origin)throw Error('External media URL');
   const res=await fetch(url.href,{cache:'reload'});
   if(!res.ok||res.status!==200||res.type==='opaque')throw Error('HTTP '+res.status);
   if(/\.(mp3|wav|m4a|ogg)$/i.test(url.pathname)){
    const type=(res.headers.get('content-type')||'').toLowerCase();
    const length=Number(res.headers.get('content-length')||0);
    if(type.includes('text/html')||(length>0&&length<500))throw Error('Invalid audio');
   }
   await cache.put(url.href,res.clone());
   if(!await cache.match(url.href))throw Error('Cache write not retained');
  }catch(e){failed.push({file:name,reason:String(e)})}
  finally{progress++;if(report)report(progress,unique.length,name,failed.length)}
 }
 return {ok:failed.length===0,count:unique.length,failed,missing:failed.length};
}
window.ExamOffline={register,saveAll};register();
})();