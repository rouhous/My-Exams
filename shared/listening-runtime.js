/* My Exams: one recording at a time. Recorded files already contain their prescribed repetitions. */
(function(){
  'use strict';
  const endActions = new Set(['back','finish','submit','end','startExam','start','randomExam','random']);
  function stopOthers(active){
    document.querySelectorAll('audio').forEach(audio=>{
      if(audio!==active && !audio.paused){
        audio.pause();
      }
    });
  }
  function stopAll(){
    document.querySelectorAll('audio').forEach(audio=>audio.pause());
    if(typeof window.stopAllNaturalPlayers==='function') window.stopAllNaturalPlayers();
  }
  function statusFor(audio){
    let status=audio.nextElementSibling;
    if(!status || !status.classList.contains('exam-listening-status')){
      status=document.createElement('div');
      status.className='exam-listening-status';
      status.setAttribute('role','status');
      status.setAttribute('aria-live','polite');
      status.style.cssText='font-size:13px;color:#36546a;margin:5px 0 12px';
      audio.insertAdjacentElement('afterend',status);
    }
    return status;
  }
  document.addEventListener('play',event=>{
    const audio=event.target;
    if(!(audio instanceof HTMLAudioElement))return;
    stopOthers(audio);
    if(!audio.classList.contains('np-audio') && typeof window.stopAllNaturalPlayers==='function'){
      window.stopAllNaturalPlayers();
    }
    if(!audio.classList.contains('np-audio')) statusFor(audio).textContent='Playing the complete listening recording. It includes the prescribed repeated reading where applicable.';
  },true);
  document.addEventListener('ended',event=>{
    const audio=event.target;
    if(audio instanceof HTMLAudioElement && !audio.classList.contains('np-audio')){
      statusFor(audio).textContent='Recording completed. You can answer or review the questions.';
    }
  },true);
  document.addEventListener('error',event=>{
    const audio=event.target;
    if(audio instanceof HTMLAudioElement && !audio.classList.contains('np-audio')){
      // Existing onerror fallback handlers may still recover; do not replace them.
      statusFor(audio).textContent='Recording unavailable. Check the offline pack or try again online.';
    }
  },true);
  document.addEventListener('click',event=>{
    const target=event.target.closest('button');
    if(target && endActions.has(target.id))stopAll();
  },true);
  document.addEventListener('visibilitychange',()=>{
    if(document.hidden)stopAll();
  });
  window.addEventListener('pagehide',stopAll);
})();
