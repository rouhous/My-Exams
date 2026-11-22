/* Regression tests for automatic feedback: option text, cloze sentence, and source evidence. */
const fs=require('fs');
const assert=require('assert');
const source=fs.readFileSync('shared/learning-feedback.js','utf8');
const document={
  createElement:()=>({style:{},setAttribute(){},append(){}}),
  head:{append(){}},documentElement:{append(){}},
  querySelectorAll:()=>[]
};
const window={location:{search:'',pathname:'/grades7-8/'}};
new Function('window','document',source)(window,document);
const api=window.MyExamsLearning;
const passage='Our drama club (1) ____ active for two years. We have practised in the theatre (2) ____ September. A famous singer is (7) ____ a concert that evening, so she cannot join us.';
const items=[
 {options:['has been','have been','is being'],answer:0},
 {options:['for','during','since'],answer:2},
 {options:['passenger','director','destination'],answer:1},
 {options:['actors','pilots','climbers'],answer:0},
 {options:['perform every','performed yesterday','are performing'],answer:2},
 {options:['had','has','have'],answer:1},
 {options:['giving','given','give'],answer:0}
];
const gap7={stem:'Gap 7',options:items[6].options,answer:0,topicType:'grammar',explanationAr:'يأتي بعد is الفعل مع ing في المضارع المستمر: is giving a concert.'};
const html=api.feedback(gap7,{skill:'grammarvocabulary',passage,items},false,'A');
assert(html.includes('Correct answer:</b> giving'),'feedback should display the answer text, not option label A');
assert(html.includes('A famous singer is giving a concert'),'gap sentence should insert the correct word');
assert(!html.includes('A famous singer is A a concert'),'gap sentence must not insert option letter');
const gap2={stem:'Gap 2',options:items[1].options,answer:2,topicType:'grammar',explanationAr:'since تحدد نقطة بداية زمنية وهي September.'};
const html2=api.feedback(gap2,{skill:'grammarvocabulary',passage,items},false,'C');
assert(html2.includes('We have practised in the theatre since September'),'gap sentence should insert since, not C');
const tf={stem:'The club will try table tennis next Saturday.',answer:'True',evidence:'Next Saturday we will try table tennis inside the centre.',explanation:'The statement agrees with this information in the reading text.'};
const html3=api.feedback(tf,{skill:'reading',passage:'Next Saturday we will try table tennis inside the centre.'},false);
assert(html3.includes('Next Saturday we will try table tennis inside the centre.'),'show stored source evidence');
assert(html3.includes('The statement agrees with this information'),'show specific stored explanation');
const short={stem:'Why did the team change their interview plan?',answers:['the guest became ill','their guest became ill']};
assert.strictEqual(api.answer(short,'A'),'the guest became ill','answer aliases should take precedence over option-label overrides');
console.log('PASS automatic feedback regression: cloze answer text, completed sentence, T/F evidence, and short-answer variants');
