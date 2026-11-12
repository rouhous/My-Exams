(()=>{
const VERSION='english-exams-v2-2026-11-12';
async function register(){if(!('serviceWorker'in navigator)||location.protocol==='file:')return false;try{await navigator.serviceWorker.register(new URL('../sw.js',location.href).href,{scope:'../'});await navigator.serviceWorker.ready;return true}catch(e){console.warn('SW registration failed',e);return false}}
async function saveAll(files,report){
 if(location.protocol==='file:')return {ok:true,mode:'zip',count:files.length,note:'الملفات مرفقة مع ZIP؛ افتح الصفحة محليًا.'};
 if(!(await register())||!('caches'in window))return {ok:false,reason:'Offline storage is not available in this browser or context'};
 const cache=await caches.open(VERSION);let i=0;const failed=[];
 for(const f of files){try{
 const path=new URL(f,location.href);if(path.origin!==location.origin){failed.push(f);continue}
 const response=await fetch(path.href,{cache:'no-store'});
 if(!response.ok)throw Error(String(response.status));await cache.put(path.href,response);
 }catch(err){failed.push(f)}finally{report&&report(++i,files.length,f,failed.length)}}
 let missing=0;for(const f of files){const u=new URL(f,location.href);if(u.origin!==location.origin||!await cache.match(u.href))missing++}
 return {ok:failed.length===0&&missing===0,count:files.length,failed,missing};
}
window.ExamOffline={register,saveAll};register();
})();