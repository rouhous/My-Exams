/* My Exams tools: pencil, eraser, selection highlighter, notes, copy, undo.
   Drawings and notes are private browser-local per page; never uploaded. */
(function(){
"use strict";
if(window.__myExamsTools)return; window.__myExamsTools=true;
const doc=document, key="my-exams-tools:"+location.pathname;
const icon={pen:"✎",eraser:"⌫",highlight:"▰",copy:"⧉",note:"▤",undo:"↶",clear:"✕",min:"−"};
let data={strokes:[],highlights:[],note:""};
try{const saved=JSON.parse(localStorage.getItem(key)||"null");if(saved&&Array.isArray(saved.strokes)&&Array.isArray(saved.highlights))data={strokes:saved.strokes,highlights:saved.highlights,note:String(saved.note||"")}}catch(e){}
let mode="",drawing=null,collapsed=false,renderPending=false;
function save(){try{localStorage.setItem(key,JSON.stringify(data))}catch(e){}}
function element(tag,className,text){const el=doc.createElement(tag);if(className)el.className=className;if(text!==undefined)el.textContent=text;return el}
function toast(message){doc.querySelector(".ex-toast")?.remove();const t=element("div","ex-toast",message);doc.body.append(t);setTimeout(()=>t.remove(),1900)}
const canvas=element("canvas","ex-ink");canvas.setAttribute("aria-label","طبقة الكتابة بالقلم");doc.body.append(canvas);
const ctx=canvas.getContext("2d");let ratio=1;
function resize(){ratio=Math.min(window.devicePixelRatio||1,2);canvas.width=Math.round(innerWidth*ratio);canvas.height=Math.round(innerHeight*ratio);canvas.style.width=innerWidth+"px";canvas.style.height=innerHeight+"px";draw()}
function draw(){
 ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,innerWidth,innerHeight);
 for(const rect of data.highlights){const y=rect.y-scrollY;if(y+rect.h<0||y>innerHeight)continue;ctx.fillStyle="rgba(255,219,47,.37)";ctx.fillRect(rect.x-scrollX,y,rect.w,rect.h)}
 for(const stroke of data.strokes){if(!stroke.points?.length)continue;ctx.strokeStyle="#ba3428";ctx.lineWidth=3;ctx.lineCap="round";ctx.lineJoin="round";ctx.beginPath();stroke.points.forEach((pt,i)=>{const x=pt.x-scrollX,y=pt.y-scrollY;if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y)});if(stroke.points.length===1){const p=stroke.points[0];ctx.lineTo(p.x-scrollX+.15,p.y-scrollY+.15)}ctx.stroke()}
}
function schedule(){if(renderPending)return;renderPending=true;requestAnimationFrame(()=>{renderPending=false;draw()})}
const bar=element("div","ex-tools");bar.setAttribute("role","toolbar");bar.setAttribute("aria-label","أدوات الدراسة");
const buttons={};
function add(id,label,handler){const b=element("button","");b.type="button";b.title=label;b.setAttribute("aria-label",label);b.innerHTML='<span class="ex-icon" aria-hidden="true">'+icon[id]+'</span><span class="ex-tool-text"></span>';b.querySelector(".ex-tool-text").textContent=label;bar.append(b);buttons[id]=b;b.addEventListener("click",handler)}
function setMode(next){mode=next===mode?"":next;canvas.classList.toggle("active",mode==="pen"||mode==="eraser");doc.body.classList.toggle("ex-ink-mode",mode==="pen"||mode==="eraser");for(const id of ["pen","eraser"])buttons[id].setAttribute("aria-pressed",String(mode===id));if(mode)toast(mode==="pen"?"ارسم على الصفحة — اضغط القلم مرة ثانية للإيقاف":"المس الرسم لمسحه — اضغط الممحاة للإيقاف")}
function selectedRects(){
 const selection=getSelection();if(!selection||selection.isCollapsed||!selection.toString().trim())return[];
 const list=[];for(let i=0;i<selection.rangeCount;i++){const range=selection.getRangeAt(i);if(bar.contains(range.commonAncestorContainer))continue;for(const r of range.getClientRects()){if(r.width>1&&r.height>3)list.push({x:r.left+scrollX,y:r.top+scrollY,w:r.width,h:r.height})}}
 return list;
}
add("highlight","تحديد",()=>{if(mode)setMode("");const rects=selectedRects();if(!rects.length){toast("حدد النص أولًا ثم اضغط تحديد");return}data.highlights.push(...rects);save();schedule();getSelection()?.removeAllRanges();toast("تم تحديد النص")});
add("pen","قلم",()=>setMode("pen"));
add("eraser","ممحاة",()=>setMode("eraser"));
add("note","أفكاري",()=>{setMode("");note.classList.toggle("visible");if(note.classList.contains("visible"))notes.focus()});
add("copy","نسخ",async()=>{if(mode)setMode("");const selected=getSelection()?.toString().trim();const text=selected||notes.value.trim();if(!text){toast("حدد النص المراد نسخه");return}try{await navigator.clipboard.writeText(text);toast("تم نسخ النص")}catch(e){try{const area=element("textarea");area.value=text;area.style.position="fixed";area.style.opacity="0";doc.body.append(area);area.select();const ok=doc.execCommand("copy");area.remove();toast(ok?"تم نسخ النص":"لم يُسمح بالنسخ")}catch(x){toast("استخدم أمر النسخ في المتصفح")}}});
add("undo","تراجع",()=>{if(data.strokes.length){data.strokes.pop()}else if(data.highlights.length)data.highlights.pop();save();schedule()});
add("clear","مسح الكل",()=>{if(!data.strokes.length&&!data.highlights.length)return;if(confirm("مسح جميع الرسومات وعلامات التحديد في هذه الصفحة؟")){data.strokes=[];data.highlights=[];save();schedule()}});
buttons.highlight.addEventListener("pointerdown",event=>event.preventDefault());buttons.copy.addEventListener("pointerdown",event=>event.preventDefault());
add("min","إخفاء",()=>{collapsed=!collapsed;for(const [id,b] of Object.entries(buttons))if(id!=="min")b.hidden=collapsed;buttons.min.setAttribute("aria-label",collapsed?"إظهار أدوات الدراسة":"إخفاء أدوات الدراسة");buttons.min.querySelector(".ex-tool-text").textContent=collapsed?"إظهار":"إخفاء";if(collapsed)setMode("")});
doc.body.append(bar);
const note=element("aside","ex-note");note.setAttribute("aria-label","ملاحظاتي");
const row=element("div","ex-heading");row.append(element("strong","", "ملاحظاتي وأفكاري"));
const close=element("button","","إغلاق");close.type="button";close.addEventListener("click",()=>note.classList.remove("visible"));row.append(close);
const notes=element("textarea");notes.placeholder="اكتب أفكارك أو مخطط الإجابة هنا...";notes.value=data.note;notes.setAttribute("aria-label","ملاحظات خاصة");notes.addEventListener("input",()=>{data.note=notes.value;save()});
const helper=element("small","","تُحفظ هذه الملاحظات على هذا الجهاز فقط، ولا تُرسل إلى الموقع.");
note.append(row,notes,helper);doc.body.append(note);
function locate(event){return {x:event.clientX+scrollX,y:event.clientY+scrollY}}
canvas.addEventListener("pointerdown",e=>{if(!["pen","eraser"].includes(mode))return;if(e.pointerType==="mouse"&&e.button!==0)return;canvas.setPointerCapture(e.pointerId);const p=locate(e);if(mode==="pen"){drawing={points:[p]};data.strokes.push(drawing)}else{eraseAt(p)}schedule();e.preventDefault()});
function distance(a,b){return Math.hypot(a.x-b.x,a.y-b.y)}
function eraseAt(p){data.strokes=data.strokes.filter(s=>!s.points.some((q,i)=>i%2===0&&distance(q,p)<19));data.highlights=data.highlights.filter(h=>!(p.x>=h.x-12&&p.x<=h.x+h.w+12&&p.y>=h.y-12&&p.y<=h.y+h.h+12))}
canvas.addEventListener("pointermove",e=>{if(!(e.buttons||e.pressure>0))return;const p=locate(e);if(mode==="pen"&&drawing){drawing.points.push(p);schedule()}if(mode==="eraser"){eraseAt(p);schedule()}});
for(const ev of ["pointerup","pointercancel"]){canvas.addEventListener(ev,()=>{if(drawing){drawing=null;save()}else if(mode==="eraser")save()})}
window.addEventListener("resize",resize);window.addEventListener("scroll",schedule,{passive:true});window.addEventListener("pagehide",save);
doc.addEventListener("keydown",e=>{if(e.key==="Escape"){setMode("");note.classList.remove("visible")}});
resize();
})();
