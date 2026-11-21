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
function evidence(expected,source,question){
 if(!source)return "";
 const parts=String(Array.isArray(source)?source.join("\n"):source).split(/\n+|(?<=[.!?])\s+/).map(s=>s.trim()).filter(Boolean);
 const key=norm(expected),tokens=key.split(" ").filter(x=>x.length>2);
 if(key&&!/^(true|false|yes|no)$/.test(key)&&tokens.length&&!(tokens.length===1&&tokens[0].length<4)){
  const matches=parts.filter(s=>{const t=norm(s),words=t.split(" ");return (" "+t+" ").includes(" "+key+" ")||(tokens.length>=2&&tokens.every(v=>words.includes(v)))});
  if(matches.length)return matches.sort((a,b)=>a.length-b.length)[0].slice(0,300);
 }
 const stop=new Set(["what","where","when","which","whose","does","did","this","that","they","them","with","have","from","into","about","should","will","would","their","there","your","were","was","does","uses","what","why","how","who","much","many","main","students","student"]);
 const qwords=[...new Set(norm(question).split(" ").filter(t=>t.length>3&&!stop.has(t)))];
 if(qwords.length<2)return "";
 const candidates=parts.map(t=>{
  const words=new Set(norm(t).split(" "));
  const found=qwords.filter(k=>words.has(k)).length;
  return {text:t,found,ratio:found/qwords.length};
 }).filter(a=>a.found>=2&&a.ratio>=0.6);
 return candidates.length?candidates.sort((a,b)=>b.ratio-a.ratio||b.found-a.found||a.text.length-b.text.length)[0].text.slice(0,300):"";
}
function completedGap(q,ctx,expected){
 const match=String(q?.stem||"").match(/\b(?:Gap|فراغ)\s*(\d+)\b/i);
 const source=String(ctx?.passage||q?.passage||"");
 if(!match||!source||!expected)return "";
 const rex=new RegExp("\\("+match[1]+"\\)\\s*_{2,}","g");
 const sentences=source.split(/(?<=[.!?])\s+|\n+/).map(x=>x.trim()).filter(Boolean);
 const line=sentences.find(x=>rex.test(x))||"";
 rex.lastIndex=0;
 return line?line.replace(rex,expected).slice(0,350):"";
}
function actualOption(q,expected,override){
 if(Array.isArray(q?.options)&&Number.isInteger(q.answer))return String(q.options[q.answer]||"");
 if(Array.isArray(q?.choices)&&Number.isInteger(q.answer))return String(q.choices[q.answer]||"");
 return String(expected||override||"");
}
function grammarArabic(q,correct,ctx){
 if(q?.ruleAr)return String(q.ruleAr);
 const sentence=completedGap(q,ctx,correct),sl=sentence.toLowerCase();
 const x=String(correct||"").toLowerCase(),opts=(q?.options||[]).map(v=>String(v).toLowerCase());
 if(x==="since"&&/\b(?:have|has)\b/.test(sl))return "نستخدم since مع المضارع التام لتحديد نقطة بداية زمنية (مثل September)، أما for فتأتي مع مدة زمنية مثل two years.";
 if(x==="for"&&/\b(?:have|has)\b/.test(sl))return "نستخدم for مع المضارع التام للدلالة على مدة زمنية، مثل for two years. أما since فتحدد نقطة البداية.";
 if(x==="giving"&&/\bis giving\b/.test(sl))return "بعد is نستخدم الفعل مع ing لتكوين المضارع المستمر؛ is giving تعني «يقدّم الآن/في الوقت المحدد». ولا نقول is give أو is given هنا.";
 if(x==="confident"&&/\bfeel(?:s)? more confident\b/.test(sl))return "بعد feel نستخدم صفة لوصف الشعور؛ confident صفة بمعنى «واثق»، أما confidence فاسم وconfidently ظرف.";
 if(x==="coming"&&/\bare coming\b/.test(sl))return "صيغة are + verb-ing تعبّر عن ترتيب مستقبلي مقرر؛ لذلك نقول are coming.";
 if(x==="forward"&&sl.includes("looking forward"))return "التعبير الثابت هو look forward to ويعني «يتطلع إلى»، ولا نستعمل look after أو look away هنا.";
 if(x==="has been"&&/\bclub\b/.test(sl))return "الفاعل المفرد club يأخذ has been في المضارع التام، مع for two years للدلالة على مدة مستمرة حتى الآن.";
 if(x==="has"&&/never performed/.test(sl))return "بعد الفاعل المفرد she نستخدم has مع التصريف الثالث: she has never performed، وهو المضارع التام.";
 if(x==="are performing"||x==="is performing")return "نستخدم am/is/are + verb-ing للتعبير عن ترتيب مستقبلي مقرر أو نشاط جارٍ، مع مراعاة توافق الفاعل والفعل.";
 if(x==="not to"&&/\btold us\b/.test(sl))return "بعد told + المفعول نستخدم not to + الفعل المجرد للنهي: told us not to throw.";
 if(x==="must"||x==="should"||x==="could"||x==="might"||x==="will")return "هذه من الأفعال الناقصة (modal verbs)، ويأتي بعدها الفعل في المصدر دون to: "+correct+" + base verb.";
 if(x==="had"&&/\b(?:before|by|already)\b/i.test(sentence))return "الماضي التام had + التصريف الثالث يبيّن أن فعلًا حدث قبل حدث آخر في الماضي.";
 if(x==="would"||x==="would do")return "في الشرط الثاني نستخدم if + past simple ثم would + الفعل المجرد للتعبير عن موقف افتراضي أو غير مؤكد.";
 if(x==="manage"&&/\bif people\b/.test(sl))return "في الشرط الأول نستخدم المضارع البسيط بعد if، ثم will في جملة النتيجة؛ ومع people يأتي الفعل بلا s.";
 if(x==="gets"&&/\bif the weather\b/.test(sl))return "في جملة الشرط الأولى يأتي الفعل في المضارع البسيط، ومع الفاعل المفرد weather نضيف s إلى gets.";
 if(x==="stay"&&/\bif visitors\b/.test(sl))return "في الشرط الأول يأتي الفعل في المضارع البسيط بعد if. والفاعل الجمع visitors يأخذ stay دون s.";
 if(x==="protect"&&/\banimals\b/.test(sl))return "مع الفاعل الجمع Animals نستخدم الفعل المجرد protect في المضارع البسيط دون s.";
 if(x==="reuse"&&sl.includes("how to"))return "بعد how to نستخدم الفعل في صورته الأساسية: how to reuse، أي «كيفية إعادة الاستخدام».";
 if(x==="second-hand")return "second-hand صفة مركبة تأتي قبل الاسم للدلالة على شيء مستعمل، مثل second-hand books.";
 if(x==="renewable")return "renewable صفة تصف نوع الطاقة قبل الاسم energy، بينما renewing صيغة فعل لا تناسب هذا التركيب.";
 if(x==="recycled")return "recycled صفة تعني «أُعيد تدويره» وتصف materials، بينما recycling تشير غالبًا إلى عملية إعادة التدوير.";
 if(x==="fall"&&/\bprices usually\b/.test(sl))return "مع الفاعل الجمع prices نستخدم المضارع البسيط fall دون s لوصف عادة أو حقيقة عامة.";
 if(x==="opens"||x==="leaves")return "نستخدم المضارع البسيط للمواعيد والجداول الثابتة، ومع الفاعل المفرد نضيف s إلى الفعل.";
 if(x==="are"&&sl.includes("going to"))return "صيغة المستقبل هي am/is/are going to + الفعل المجرد؛ الفاعل we يأخذ are.";
 if(x==="going"&&sl.includes("going to"))return "صيغة be going to + الفعل المجرد تُستخدم للخطة أو النية المستقبلية.";
 if(x==="had"&&opts.includes("has")&&opts.includes("have"))return "نستخدم had + التصريف الثالث عندما نعبّر عن فعل اكتمل قبل فعل آخر في الماضي.";
 if(x==="will finish")return "بعد hope نستطيع استخدام will + الفعل المجرد للتعبير عن توقع أو أمل متعلق بالمستقبل.";
 if(x==="himself"||x==="ourselves")return "نستخدم الضمير الانعكاسي عندما يعود الفعل على الفاعل نفسه: himself للمفرد المذكر، وourselves للمتكلم الجمع.";
 if(x==="but")return "but أداة ربط تفيد التباين بين فكرتين؛ نستعملها هنا للربط بين الاستمتاع بالرحلة والالتزام بالتعليمات.";
 if((opts.includes("was")&&opts.includes("were"))||(opts.includes("is")&&opts.includes("are")))return "تتغير صيغة الفعل be بحسب الفاعل: المفرد يأخذ is/was والجمع يأخذ are/were.";
 if(/_{2,}/.test(q?.stem||""))return "تحدَّد الصيغة الصحيحة من وظيفة الكلمة في الجملة وزمن الفعل والفاعل.";
 return "";
}

function rule(q,expected,ctx){
 const known=q?.rule||q?.grammarRule||q?.explanation||q?.feedback;
 if(typeof known==="string"&&known.trim())return known;
 const filled=completedGap(q,ctx,expected);
 const opts=(q?.options||[]).map(x=>String(x).toLowerCase());
 if(/\bdid not\b/i.test(filled))return "Past simple negative: use did not + base verb (e.g., did not remove).";
 if(/\bif\b/i.test(filled)&&/\bwill\b/i.test(filled))return "First conditional: If + present simple, will + base verb for a likely future result.";
 if(/\b(?:was|were)\s+\w+ed\b/i.test(filled))return "Passive voice or past continuous depends on the verb form: past be + past participle describes an action done to the subject.";
 if((opts.includes("was")&&opts.includes("were"))||(opts.includes("is")&&opts.includes("are")))return "Subject–verb agreement: use is/was with a singular subject, and are/were with a plural subject.";
 if(/\byesterday\b/i.test(filled)&&opts.includes("buy")&&opts.includes("bought"))return "Past simple: use ‘bought’ (past of buy) for an action completed yesterday.";
 if(opts.includes("should")&&opts.includes("should to"))return "Modal verb: ‘should’ is followed directly by a base verb, not ‘should to’.";
 const s=String(q?.stem||"").toLowerCase();
 if(/\bthan\b/.test(s)&&/more\b|er$|ier$|better|worse/i.test(expected))return "Comparatives: use the comparative form with ‘than’ to compare two things (-er, -ier or more + adjective/adverb).";
 if(/\b(?:should|must|can|could|will|may)\s+_{2,}/.test(s))return "After a modal verb (can, should, must), use the base form of the verb.";
 if(/\bto\s+_{2,}/.test(s))return "Use the base form of the verb after ‘to’ in a to-infinitive.";
 return "";
}
const GLOSSES={
"blog":"مدوّنة","platform":"منصّة إلكترونية","upload":"يرفع ملفًا على الإنترنت",
"private":"خاصّ / سرّي","source":"مصدر","drought":"جفاف","heatwave":"موجة حر",
"greenhouse gas":"غاز دفيئة","carbon footprint":"البصمة الكربونية","sea level":"مستوى سطح البحر",
"solar panel":"لوح شمسي","wind turbine":"توربين رياح","hydropower":"طاقة كهرومائية",
"battery":"بطارية","grid":"شبكة الكهرباء","archaeologist":"عالم آثار",
"excavation":"تنقيب أثري","artefact":"قطعة أثرية","trade route":"طريق تجاري","heritage":"تراث"
};
function explanation(q,ctx={},override){
 const expected=answer(q,override),type=String(ctx.skill||ctx.key||q?.skill||"").toLowerCase();
 const correct=actualOption(q,expected,override);
 const category=String(q?.topicType||q?.category||"").toLowerCase();
 const spoken=/listen|lst/.test(type),grammar=category==="grammar"||(!category&&/gram|^grm$|cloze/.test(type));
 const vocab=category==="vocabulary"||(!category&&/vocab|^vcb$|spell|word/.test(type)&&!grammar);
 const tf=/^(true|false)$/i.test(String(expected).trim());
 const source=q?.script||q?.transcript||q?.passage||ctx.script||ctx.transcript||ctx.passage||ctx.text||"";
 const evidenceText=q?.evidence||q?.sourceQuote||evidence(correct,source,q?.stem||"");
 const selected=(Array.isArray(q?.options)&&Number.isInteger(q.answer))?q.options[q.answer]:"";
 const expanded=ctx.correctText||((/^[A-F]$/i.test(expected)&&selected)?selected:"");
 const sentence=completedGap(q,ctx,correct);
 const ar=typeof q?.explanationAr==="string"&&q.explanationAr.trim()?q.explanationAr.trim():"";
 let reasonAr=ar;
 if(!reasonAr){
  if(grammar)reasonAr=grammarArabic(q,correct,ctx);
  else if(vocab)reasonAr=q?.meaningAr?
    "الكلمة «"+correct+"» تعني «"+q.meaningAr+"» في هذا السياق؛ وهي الأنسب لمعنى الجملة.":
    "نختار «"+correct+"» لأن معناها أو وظيفتها تناسب سياق الجملة، وليست مجرد كلمة تشبه الاختيارات الأخرى.";
  else if(tf)reasonAr=expected.toLowerCase()==="true"?
    "العبارة صحيحة لأنها تتفق مع المعلومة المذكورة في النص أو التسجيل.":
    "العبارة خاطئة؛ المعلومة الواردة في النص أو التسجيل تختلف عن مضمونها. قارنها بالدليل أسفل التصحيح.";
  else if(spoken)reasonAr="الإجابة تعتمد على ما قاله المتحدث فعلًا في التسجيل. راجع المعلومة الأساسية ولا تعتمد على الكلمات المشتتة في الخيارات.";
  else if(/read|match/.test(type))reasonAr="الإجابة الصحيحة هي التي يثبتها مضمون النص. قارنها بالمعلومة الداعمة أدناه إن كانت متاحة.";
  else reasonAr="قارن الإجابة الصحيحة بالسؤال ولاحظ الكلمات التي تحدد المعنى.";
 }
 let reasonEn=typeof q?.explanation==="string"?q.explanation.trim():"";
 if(!reasonEn&&tf)reasonEn=expected.toLowerCase()==="true"?"This statement matches the source.":"This statement contradicts the source.";
 const ruleAr=grammar?(q?.ruleAr||grammarArabic(q,correct,ctx)):"";
 const meaning=vocab?q?.meaningAr||q?.arabicMeaning||q?.definition||q?.meaning||GLOSSES[norm(correct)]||"":"";
 const example=sentence||(grammar&&/_{2,}/.test(q?.stem||"")?String(q.stem).replace(/_{2,}/,correct):"");
 return {expected,expanded,correct,reasonAr,reasonEn,ruleAr,
   meaning,example,evidence:evidenceText,kind:spoken?"Listening script":"Reading text"};
}
function feedback(q,ctx={},ok=false,override){
 const p=explanation(q,ctx,override);
 let html='<div class="mex-fb '+(ok?"mex-fb-ok":"mex-fb-try")+'" role="note"><strong>'+(ok?"✓ Excellent! أحسنت، واصل.":"✗ لنصحح الإجابة معًا · Let’s correct it!")+'</strong>';
 const display=p.expected&&/^[A-F]$/i.test(p.expected)&&p.correct&&p.correct!==p.expected?p.expected+' — '+p.correct:p.correct||p.expected;
 if(display)html+='<p><b>الإجابة الصحيحة · Correct answer:</b> '+esc(display)+'</p>';
 if(p.reasonAr)html+='<p dir="rtl" class="mex-fb-ar"><b>لماذا هذه الإجابة؟</b> '+esc(p.reasonAr)+'</p>';
 if(p.ruleAr && p.ruleAr!==p.reasonAr)html+='<p dir="rtl" class="mex-fb-ar"><b>القاعدة:</b> '+esc(p.ruleAr)+'</p>';
 if(p.meaning)html+='<p dir="rtl" class="mex-fb-ar"><b>معنى الكلمة:</b> '+esc(p.correct)+' = '+esc(p.meaning)+'</p>';
 if(p.example)html+='<p><b>الجملة بعد التصحيح:</b> <span lang="en">'+esc(p.example)+'</span></p>';
 if(p.evidence){
  const quote=esc(p.evidence),pos=p.correct?p.evidence.toLowerCase().indexOf(p.correct.toLowerCase()):-1;
  let highlighted=quote;
  if(pos>=0&&p.correct)highlighted=esc(p.evidence.slice(0,pos))+'<mark>'+esc(p.evidence.slice(pos,pos+p.correct.length))+'</mark>'+esc(p.evidence.slice(pos+p.correct.length));
  html+='<p dir="rtl" class="mex-fb-ar"><b>الدليل من '+(p.kind==="Listening script"?"نص الاستماع":"نص القراءة")+':</b></p><blockquote lang="en">'+highlighted+'</blockquote>';
 }
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
'.mex-fb-ar{direction:rtl;text-align:right;line-height:1.8;font-size:14px}.mex-fb mark{background:#ffdb63;padding:1px 2px;border-radius:2px;color:#263b27}.mex-fb-try{background:#fff8ef;border-color:#ead7b2;border-left-color:#b78839;color:#503b20}.mex-fb p{margin:6px 0}.mex-fb blockquote{margin:6px 0;padding:9px;background:#fff;border-left:3px solid #be9d50}.mex-fb-note{font-size:12px;color:#60766c}',
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
  const status=d.createElement("p");status.className="mex-ai-status";status.textContent="تقدير تدريبي فقط. عند الضغط يُرسل النص إلى خدمة AI للمراجعة؛ لا تُدخل بيانات شخصية.";
  const result=d.createElement("div");result.className="mex-ai-result";
  panel.append(button,status,result);ta.insertAdjacentElement("afterend",panel);
  button.addEventListener("click",async()=>{
   const mode=String(d.querySelector("#mode")?.value||"").toLowerCase();
   const fullExam=["exam","full","random"].includes(mode);
   const finishControl=d.querySelector("#submit,#end,#finish,#finishBtn");
   if((fullExam||(!mode&&finishControl))&&finishControl&&!finishControl.disabled){
     status.textContent="تظهر مراجعة AI بعد تسليم الاختبار الكامل. في تدريب المهارة يمكنك طلبها مباشرة.";
     return;
   }
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
