/* My Exams: preserve real question inputs while splitting long reading and cloze sources.
   Safe to call repeatedly after dynamic exam rendering; no data or answer keys modified. */
(function(){
"use strict";
if(window.__myExamsSplitPanels)return;window.__myExamsSplitPanels=true;
const selector=".section,.task,.part,.exam-dual-candidate";
function enhance(){
 for(const section of document.querySelectorAll(selector)){
   if(section.dataset.dualReady==="yes")continue;
   const children=[...section.children];
   const sources=children.filter(el=>el.matches(".passage,.paired,.two-col,.source-text"));
   // Reading 1 may present several texts with explicit "Text 1" labels.
   // Keep those labels with their respective passages when moving them.
   for(const source of [...sources]){const prev=source.previousElementSibling;if(prev&&prev.tagName==="P"&&/^Text\\s+\\d+\\s*$/i.test(prev.textContent.trim())&&!sources.includes(prev))sources.push(prev)}
   const questions=children.filter(el=>el.matches(".question,.q"));
   if(!sources.length||questions.length<2)continue;
   // Never split scripts hidden inside teacher-only listening details.
   const raw=sources.map(el=>el.textContent||"").join(" ");
   if(raw.trim().length<90 && questions.length<5)continue;
   const first=Math.min(...sources.map(el=>children.indexOf(el)),...questions.map(el=>children.indexOf(el)));
   const grid=document.createElement("div");grid.className="exam-dual-grid";
   const reference=document.createElement("div");reference.className="exam-dual-panel exam-reference";
   const exercise=document.createElement("div");exercise.className="exam-dual-panel exam-questions";
   reference.tabIndex=0;exercise.tabIndex=0;
   reference.setAttribute("role","region");exercise.setAttribute("role","region");
   reference.setAttribute("aria-label","نص القراءة، تمرير مستقل");
   exercise.setAttribute("aria-label","أسئلة النشاط، تمرير مستقل");
   function heading(text){const h=document.createElement("strong");h.className="exam-dual-heading";h.textContent=text;return h}
   reference.append(heading("النص · Reading Text"));
   exercise.append(heading("الأسئلة · Questions"));
   const insertBefore=children[first];
   section.insertBefore(grid,insertBefore);grid.append(reference,exercise);
   // Move original DOM nodes, rather than cloning them, to preserve event listeners,
   // radio selections, writing state, marking hooks and accessibility IDs.
   for(const source of sources)reference.append(source);
   for(const question of questions)exercise.append(question);
   section.dataset.dualReady="yes";
 }
}
let scheduled=false;
function queue(){if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;enhance()})}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",queue,{once:true});else queue();
const watch=new MutationObserver(items=>{
 if(items.some(item=>[...item.addedNodes].some(node=>node.nodeType===1 &&
    (node.matches?.(selector)||node.querySelector?.(selector)||node.matches?.(".passage,.question,.q")))))queue();
});
watch.observe(document.documentElement,{subtree:true,childList:true});
window.MyExamsSplitPanels={refresh:queue};
})();
