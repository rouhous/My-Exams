let activeNaturalPlayer=null;
function renderNaturalPlayer(id,backup){return `<div class="naturalplayer" data-natural="${id}"><b>Natural English audio · ${id.endsWith('L2')?'Two-speaker interview':'Five illustrated short texts'}</b><p class="np-fallback">Natural MP3 files are hosted by My Exams. Download this exam pack for offline listening. Instructions are spoken once; the texts are played twice.</p><button type="button" class="np-start">▶ Play natural recording</button><button type="button" class="np-pause" disabled>⏸ Pause</button><button type="button" class="np-stop" disabled>■ Stop</button><div class="np-status" role="status" aria-live="polite">Ready</div><progress max="1" value="0"></progress><audio class="np-audio" preload="none" style="display:none"></audio><details><summary>Offline backup MP3</summary><audio controls preload="none" src="${backup}"></audio></details></div>`}
function stopAllNaturalPlayers(){if(activeNaturalPlayer){activeNaturalPlayer.stop();activeNaturalPlayer=null}}
function setupNaturalPlayers(){document.querySelectorAll('[data-natural]').forEach(root=>{
 const cfg=NATURAL_AUDIO[root.dataset.natural],player=root.querySelector('.np-audio'),start=root.querySelector('.np-start'),pause=root.querySelector('.np-pause'),stop=root.querySelector('.np-stop'),status=root.querySelector('.np-status'),progress=root.querySelector('progress');
 const sequence=[{...cfg.intro,label:'Instruction',pause:1000}];for(let round=0;round<cfg.rounds;round++)cfg.segments.forEach((seg,i)=>sequence.push({...seg,label:`Round ${round+1}: ${seg.label}`,pause:(i===cfg.segments.length-1?(round<cfg.rounds-1?cfg.repeatPauseMs:0):cfg.pauseMs)}));
 let idx=-1,timeout=null,remaining=0,waitSince=0,paused=false,disposed=false,playing=false,generation=0;
 const update=t=>{if(!disposed)status.textContent=t};
 const clearWait=()=>{if(timeout!==null){clearTimeout(timeout);timeout=null}};
 const setButtons=on=>{start.disabled=on;pause.disabled=!on;stop.disabled=!on};
 const reset=()=>{generation++;clearWait();player.pause();player.removeAttribute('src');player.load();idx=-1;remaining=0;paused=false;playing=false;pause.textContent='⏸ Pause';setButtons(false);progress.value=0};
 const showCurrent=()=>{progress.max=sequence.length;progress.value=Math.max(0,idx);};
 const playCurrent=async()=>{if(disposed||idx<0||idx>=sequence.length)return;const mygen=generation; const item=sequence[idx];remaining=0;playing=true;update('Playing '+item.label);player.src=item.url;player.load();try{await player.play()}catch(e){if(mygen!==generation)return;update('Natural audio unavailable. Download the offline pack or use the provisional backup below.');playing=false;setButtons(false)}};
 const waitThenPlay=ms=>{remaining=ms;waitSince=Date.now();playing=false;update('Pause '+(ms/1000).toFixed(ms%1000?1:0)+' seconds');if(!paused)timeout=setTimeout(()=>{timeout=null;if(!paused)playCurrent()},ms)};
 const ended=()=>{if(disposed||idx<0||paused)return;const last=sequence[idx];idx++;showCurrent();if(idx>=sequence.length){update('Completed: recording played twice.');setButtons(false);activeNaturalPlayer=null;playing=false;return}waitThenPlay(last.pause||0)};
 player.addEventListener('ended',ended);
 const stopPlayer=()=>{reset();update('Stopped')};
 start.onclick=()=>{stopAllNaturalPlayers();activeNaturalPlayer={stop:stopPlayer};reset();idx=0;showCurrent();setButtons(true);playCurrent()};
 pause.onclick=()=>{if(idx<0)return;if(!paused){paused=true;if(timeout!==null){clearWait();remaining=Math.max(0,remaining-(Date.now()-waitSince))}else player.pause();pause.textContent='▶ Resume';update('Paused')}else{paused=false;pause.textContent='⏸ Pause';if(remaining>0)waitThenPlay(remaining);else if(playing)player.play().catch(()=>update('Could not resume; try offline backup'));else playCurrent()}};
 stop.onclick=stopPlayer;
 player.addEventListener('error',()=>{if(idx>=0&&!paused)update('Natural recording unavailable: download its offline files or use backup MP3.')});
 root._disposeNatural=()=>{disposed=true;reset()};
 })}
