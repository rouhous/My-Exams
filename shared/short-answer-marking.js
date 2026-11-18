/* English short answer marking for My Exams.
   Accept the expected answer as a complete contiguous phrase, with up to four
   words above the question's stated maximum. This checks text, not meaning. */
(function(g){
"use strict";
function words(value){
 return String(value==null?"":value)
 .normalize("NFKC").toLowerCase().replace(/[’‘]/g,"'")
 .replace(/\b(\d+)\s*[-–]\s*(\d+)\b/g,"$1 $2")
 .replace(/[^\p{L}\p{N}]+/gu," ").trim().split(/\s+/).filter(Boolean);
}
function evaluate(value,question){
 const typed=words(value),limit=Number(question&&question.maxWords);
 const maxWords=Number.isFinite(limit)&&limit>0?Math.floor(limit):4;
 const permitted=maxWords+4;
 const variants=[...(Array.isArray(question&&question.answers)?question.answers:[]),question&&question.answer]
   .filter(x=>typeof x==="string"&&x.trim()).flatMap(x=>x.split(/\s+(?:\/|\bor\b)\s+/i));
 const reference=variants.length?variants[0]:"";
 if(!typed.length)return {correct:false,reason:"empty",wordCount:0,maxWords,permitted,reference};
 if(typed.length>permitted)return {correct:false,reason:"too-long",wordCount:typed.length,maxWords,permitted,reference};
 for(const v of variants){
  const target=words(v);
  if(!target.length)continue;
  for(let i=0;i<=typed.length-target.length;i++){
   if(target.every((word,j)=>typed[i+j]===word)){
    return {correct:true,reason:"matched",wordCount:typed.length,maxWords,permitted,reference};
   }
  }
 }
 return {correct:false,reason:variants.length?"no-match":"manual",wordCount:typed.length,maxWords,permitted,reference};
}
g.MyExamsShortAnswers={evaluate,words};
})(window);
