/* My Exams: source-grounded per-question feedback + shared MEJ AI writing review. */
(function(w,d){
"use strict";
if(w.MyExamsLearning)return;
const API="https://xboracsbzikojobumcke.supabase.co/functions/v1/mej-writing-ai";
const esc=x=>String(x==null?"":x).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const norm=x=>String(x==null?"":x).normalize("NFKC").toLowerCase().replace(/[’‘]/g,"'").replace(/[^\p{L}\p{N}]+/gu," ").trim().replace(/\s+/g," ");
function answer(q,override){
 if(typeof override==="string"&&override.trim())return override;
 if(Array.isArray(q?.options)&&Number.isInteger(q.answer))return String(q.options[q.answer]??"");
 if(Array.isArray(q?.choices)&&Number.isInteger(q.answer))return String(q.choices[q.answer]??"");
 if(Array.isArray(q?.answers))return String(q.answers[0]||"");
 return typeof q?.answer==="string"?q.answer:typeof q?.answer==="boolean"?(q.answer?"True":"False"):"";
}
function evidence(expected,source){
 if(!expected||!source)return "";
 const parts=String(Array.isArray(source)?source.join("\n"):source).split(/\n+|(?<=[.!?])\s+/).map(s=>s.trim()).filter(Boolean);
 const key=norm(expected),tokens=key.split(" ").filter(x=>x.length>2);
 if(!tokens.length||(tokens.length===1&&tokens[0].length<4))return "";
 const matches=parts.filter(s=>{const t=norm(s),words=t.split(" ");return (" "+t+" ").includes(" "+key+" ")||(tokens.length>=2&&tokens.every(v=>words.includes(v)))});
 return matches.length?matches.sort((a,b)=>a.length-b.length)[0].slice(0,300):"";
}
function rule(q,expected){
 const known=q?.rule||q?.grammarRule||q?.explanation||q?.feedback;
 if(typeof known==="string"&&known.trim())return known;
 const s=String(q?.stem||"").toLowerCase();
 if(/\bthan\b/.test(s)&&/more\b|er$|ier$|better|worse/i.test(expected))return "Comparatives: use the comparative form with ‘than’ to compare two things (-er, -ier or more + adjective/adverb).";
 if(/\b(?:should|must|can|could|will|may)\s+_{2,}/.test(s))return "After a modal verb (can, should, must), use the base form of the verb.";
 if(/\bto\s+_{2,}/.test(s))return "Use the base form of the verb after ‘to’ in a to-infinitive.";
 return "";
}
function explanation(q,ctx={},override){
 const expected=answer(q,override),type=String(ctx.skill||ctx.key||q?.skill||"").toLowerCase();
 return {expected,rule:/gram/.test(type)?rule(q,expected):"",
   meaning:/vocab|spell|word/.test(type)?q?.meaningAr||q?.arabicMeaning||q?.definition||q?.meaning||( /_{2,}/.test(q?.stem||"")?String(q.stem).replace(/_{2,}/,expected):""):"",
   example:/vocab|spell|word/.test(type)&&/_{2,}/.test(q?.stem||"")&&(q?.meaningAr||q?.arabicMeaning||q?.definition||q?.meaning)?String(q.stem).replace(/_{2,}/,expected):"",
   evidence:q?.evidence||q?.sourceQuote||evidence(expected,q?.script||q?.transcript||q?.passage||ctx.script||ctx.transcript||ctx.passage||ctx.text||""),
   kind:/listen|lst/.test(type)?"Listening script":"Reading text"};
}
function feedback(q,ctx={},ok=false,override){
 const p=explanation(q,ctx,override);
 let html='<div class="mex-fb '+(ok?"mex-fb-ok":"mex-fb-try")+'" role="note"><strong>'+(ok?"✓ Excellent! أحسنت، واصل.":"✗ Try again! حاول مرة أخرى.")+'</strong>';
 if(p.expected)html+='<p><b>Correct answer:</b> '+esc(p.expected)+'</p>';
 if(p.rule)html+='<p><b>Grammar rule:</b> '+esc(p.rule)+'</p>';
 if(p.meaning)html+='<p><b>Word meaning:</b> '+esc(p.meaning)+'</p>';
 if(p.example)html+='<p><b>Example:</b> '+esc(p.example)+'</p>';
 if(p.evidence){
  let quote=esc(p.evidence);
  const pos=p.evidence.toLowerCase().indexOf(p.expected.toLowerCase());
  if(pos>=0&&p.expected){quote=esc(p.evidence.slice(0,pos))+'<mark>'+esc(p.evidence.slice(pos,pos+p.expected.length))+'</mark>'+esc(p.evidence.slice(pos+p.expected.length))}
  html+='<p><b>From the '+esc(p.kind)+':</b></p><blockquote>'+quote+'</blockquote>';
 }
 if(!p.rule&&!p.meaning&&!p.example&&!p.evidence)html+='<p class="mex-fb-note">Compare your response with the reference answer. No verified explanation or source sentence was stored for this item.</p>';
 return html+'</div>';
}
function pageGrade(){
 const url=new URLSearchParams(w.location?.search||"");
 const grade=Number(url.get("grade"));if(grade>=5&&grade<=12)return grade;
 const track=String(url.get("track")||"");if(/^11(?:-|$)/.test(track))return 11;if(/^12(?:-|$)/.test(track))return 12;
 const path=(w.location?.pathname||"").match(/grade[-_]?(\d+)|grades(\d+)-(\d+)/i);
 if(path)return Number(path[1]||path[2]);
 const el=d.querySelector("#grade");if(el&&Number(el.value)>=5)return Number(el.value);
 return 12;
}
function genre(prompt){
 const s=String(prompt).toLowerCase();
 if(/\bemail\b|\bletter\b|رسالة|بريد/.test(s))return "email";
 if(/\bstory\b|\bnarrative\b|beginning:|قص[ةص]/.test(s))return "story";
 if(/\bchart\b|\bgraph\b|\bdata\b|\bpercentages?\b|رسم بياني/.test(s))return "description";
 if(/\bopinion\b|\bdiscuss\b|\bevaluate\b|\badvantages?\b|\bdisadvantages?\b/.test(s))return "opinion";
 return "informative";
}
function metadata(ta){
 const box=ta.closest("section,.part,.writing-task,.question")||ta.parentElement;
 const candidates=[...(box?.querySelectorAll?.(".prompt,.qstem,.writing-prompt,p,.notice")||[])].map(el=>(el.textContent||"").trim()).filter(Boolean);
 const taskLine=candidates.find(v=>v.length>35&&/write|describe|summaris|summariz|discuss|evaluate|compare|essay|email|اكتب|تحدث عن/i.test(v));
 const prompt=(taskLine||ta.previousElementSibling?.textContent||candidates.find(v=>v.length>25)||box?.textContent||"").trim().slice(0,320);
 return {grade:pageGrade(),genre:genre(prompt),topic:prompt.length>=8?prompt:"Complete the English writing task."};
}
const style=d.createElement("style");style.id="mex-feedback-style-v1";
style.textContent=[
'.mex-fb{font:14px/1.6 system-ui,Arial,sans-serif;direction:ltr;text-align:left;margin:9px 0 12px;padding:11px 13px;border:1px solid #b8d5c7;border-left:4px solid #0a7859;border-radius:10px;background:#f2faf5;color:#1b4036}',
'.mex-fb mark{background:#ffdb63;padding:1px 2px;border-radius:2px;color:#263b27}.mex-fb-try{background:#fff8ef;border-color:#ead7b2;border-left-color:#b78839;color:#503b20}.mex-fb p{margin:6px 0}.mex-fb blockquote{margin:6px 0;padding:9px;background:#fff;border-left:3px solid #be9d50}.mex-fb-note{font-size:12px;color:#60766c}',
'.mex-ai-panel{margin:12px 0 18px;padding:12px;border:1px solid #b8d5c7;border-radius:12px;background:#f7fcf8;direction:rtl;text-align:right}',
'.mex-ai-trigger{min-height:44px;padding:9px 14px;border:0;border-radius:9px;background:#0b6348;color:white;font:700 14px system-ui,sans-serif;cursor:pointer}.mex-ai-trigger:disabled{opacity:.55;cursor:wait}',
'.mex-ai-status{font:13px/1.6 system-ui,sans-serif;margin:7px 0}.mex-ai-result{font:14px/1.65 system-ui,sans-serif;overflow-wrap:anywhere}',
'.mex-ai-result h4{font-size:16px;margin:9px 0;color:#0d573e}.mex-ai-result li{margin:11px 0;padding:6px;border-bottom:1px solid #dce8db}.mex-ai-result p{margin:5px 0}',
'@media print{.mex-ai-trigger{display:none!important}.mex-fb,.mex-ai-panel{break-inside:avoid}}'
].join("\n");(d.head||d.documentElement).append(style);
const seen=new WeakSet();
function mount(){
 d.querySelectorAll("textarea").forEach(ta=>{
  if(seen.has(ta)||ta.closest(".ex-note,.mex-ai-panel")||ta.disabled)return;
  const surroundings=(ta.closest("section,.part,.writing-task")?.textContent||"").toLowerCase();
  if(!ta.matches("[data-writing],[data-write],textarea[name^='wrt'],textarea[name^='writing'],textarea[name='dataAnalysis'],textarea[id^='write'],textarea[data-k$=':text']")&&!/writing|essay|story|paragraph|email|chart|write at least|اكتب|الكتابة/.test(surroundings))return;
  seen.add(ta);
  const panel=d.createElement("div");panel.className="mex-ai-panel";
  const button=d.createElement("button");button.type="button";button.className="mex-ai-trigger";button.textContent="✨ راجع كتابتي بالذكاء الاصطناعي · AI Writing Feedback";
  const status=d.createElement("p");status.className="mex-ai-status";status.textContent="تقدير تدريبي فقط — تصحيح المعلم هو المرجع.";
  const result=d.createElement("div");result.className="mex-ai-result";
  panel.append(button,status,result);ta.insertAdjacentElement("afterend",panel);
  button.addEventListener("click",async()=>{
   const value=ta.value.trim(),info=metadata(ta);
   if(value.length<50){status.textContent="اكتب 50 حرفًا على الأقل قبل طلب المراجعة.";return}
   if(value.length>7000){status.textContent="الحد الأقصى 7000 حرف.";return}
   if(w.navigator&&w.navigator.onLine===false){status.textContent="مراجعة AI تحتاج إنترنت؛ يمكنك الاحتفاظ بالنص دون إرسال.";return}
   button.disabled=true;status.textContent="جارٍ تحليل الكتابة...";result.textContent="";
   const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),30000);
   try{
    const maxScore=info.grade<=9?5:10;
    const response=await fetch(API,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:value,topic:info.topic,genre:info.genre,grade:info.grade,maxScore}),signal:controller.signal,cache:"no-store"});
    const json=await response.json().catch(()=>({}));
    if(!response.ok||json.ok!==true||!json.feedback||!Array.isArray(json.feedback.five_points)||json.feedback.five_points.length!==5)throw Error(json.message||"Service unavailable");
    const f=json.feedback;
    const score=json.score&&Number.isFinite(Number(json.score.value))?Number(json.score.value):(maxScore===10?Number(f.score5)*2:Number(f.score5));
    let html='<h4>التقدير التدريبي: '+esc(score)+' / '+maxScore+'</h4><p>'+esc(f.summary)+'</p><p>'+esc(f.score_reason)+'</p><ol>';
    f.five_points.forEach(p=>{html+='<li><b>'+esc(p.category)+'</b><p>✓ '+esc(p.what_works)+'</p><p>↗ '+esc(p.what_to_improve)+'</p>'+(p.short_example?'<p>Example: '+esc(p.short_example)+'</p>':"")+'</li>'});
    html+='</ol><p><strong>الخطوة التالية: </strong>'+esc(f.next_step)+'</p><small>درجة تقديرية تدريبية وليست تقييمًا رسميًا. لا تُدخل بيانات شخصية في موضوع الكتابة.</small>';
    result.innerHTML=html;status.textContent="اكتملت المراجعة.";
   }catch(e){status.textContent="تعذّرت مراجعة AI: "+String(e?.message||"Service unavailable").slice(0,150)+". لم تُمنح درجة غير مؤكدة."}
   finally{clearTimeout(timer);button.disabled=false}
  });
 });
}
function boot(){mount();if(w.MutationObserver){const o=new MutationObserver(()=>mount());o.observe(d.body,{subtree:true,childList:true})}}
if(d.readyState==="loading")d.addEventListener("DOMContentLoaded",boot);else if(d.body)boot();
w.MyExamsLearning={feedback,answer,evidence,explanation,mount,metadata};
})(window,document);
