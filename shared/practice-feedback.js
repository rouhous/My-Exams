/* My Exams — source-grounded feedback, never auto-invent a rule or quotation.
   Call only after checking one answer in practice, or after full exam submission. */
(function(global){
  "use strict";
  function escapeText(value){
    return String(value == null ? "" : value).replace(/[&<>"']/g,function(ch){
      return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch];
    });
  }
  function line(title,value,extra){
    if(value===undefined || value===null || String(value).trim()==="")return "";
    return '<div style="margin-top:5px"><strong>'+escapeText(title)+'</strong> <span'+(extra||"")+'>'+escapeText(value)+'</span></div>';
  }
  function render(details){
    const d=details||{},ok=Boolean(d.correct);
    const explanation=d.explanation || "";
    const evidence=d.evidence || "";
    return '<div class="exams-answer-feedback" role="status" aria-live="polite" style="border:1px solid #afc5cc;border-left:4px solid '+(ok?'#246d54':'#9a611e')+';border-radius:9px;padding:11px 13px;margin:8px 0;background:#f6faf9;line-height:1.6">'
      +'<strong>'+(ok?'✓ Correct':'✗ Review your answer')+'</strong>'
      +line("Your answer:",d.yourAnswer===undefined?"Not answered":d.yourAnswer)
      +line("Correct answer:",d.correctAnswer)
      +(explanation?line("Why?",explanation):'')
      +(evidence?line("Evidence from the text:",evidence,' dir="ltr"'): '')
      +(d.retryHint?line("Try again tip:",d.retryHint):"")
      +'</div>';
  }
  global.MyExamsFeedback={render:render,escape:escapeText};
})(window);
