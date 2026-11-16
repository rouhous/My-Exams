#!/usr/bin/env python3
"""Build missing Oman Grade 11 Core unit papers 1, 3 and 4 from new thematic content.
Original teacher-review practice, not Ministry-certified textbook content.
"""
import json, pathlib, copy
R=pathlib.Path(__file__).resolve().parents[1]
D=R/"grade11/core/units"
base=json.loads((D/"unit2-paper-b.json").read_text())
ref_html=(D/"paper-b-preview.html").read_text()
units={
1:dict(title="Communication",subject="communication",club="media club",project="student news bulletin",venue="media room",expert="English teacher",error="an incorrect activity date",evidence="the official school calendar"),
3:dict(title="Travellers and Tourists",subject="tourism",club="heritage club",project="local walking route",venue="old souq",expert="local guide",error="an incorrect street name",evidence="the road sign"),
4:dict(title="Innovation",subject="innovation",club="science club",project="electricity-saving sensor",venue="science laboratory",expert="school engineer",error="an unreliable movement reading",evidence="the recorded test results")
}
def W(s):return len(s.split())
def pad(s,lo,hi):
  additions=[
  "Our teacher encouraged every student to record sources and explain the evidence before making public claims.",
  "We also compared different ideas, invited questions and made sure our explanations were accessible to younger pupils.",
  "Different people contributed through research, writing, careful planning and respectful discussion of unexpected problems.",
  "The group learned that correcting an error is a responsible choice rather than a reason for embarrassment.",
  "Parents appreciated being able to ask questions and receive clear answers supported by reliable information.",
  "This experience showed why patience and independent checking matter just as much as creative ideas.",
  "Our group agreed to review the final version carefully before sharing it with other classes.",
  "The teachers reminded us that every useful project needs an honest explanation of its limitations.",
  "These habits can help students in other subjects and in future community activities.",
  "We kept our records so that other learners could understand the decisions we made.",
  ]
  for s2 in additions:
    if W(s)>=lo:break
    allowed=hi-W(s)
    if allowed<=0:break
    if W(s2)>allowed:continue
    s+=" "+s2
  if not lo<=W(s)<=hi:raise ValueError(f"Word length {W(s)} outside {lo}-{hi}")
  return s
def mc(stem,choices,answer):return dict(type="mc",stem=stem,options=choices,answer=answer)
def tf(stem,truth):return dict(type="tf",stem=stem,options=["True","False"],answer=0 if truth else 1)
def short(stem,answer):return dict(type="short",stem=stem,answer=answer,maxWords=4)
for number,x in units.items():
  u=copy.deepcopy(base);u["id"]=f"g11-core-u{number}-original"
  u["unit"]={"number":number,"title":x["title"]}
  u["status"]="original_nine_section_teacher_review_draft"
  u["certifiedTextbookMatch"]=u["readyForStudentExam"]=False
  u["listeningSources"]=[f"unit{number}-listening{i}-original-draft.json" for i in (1,2)]
  s=u["sections"]
  s["grm"]["passage"]=f"""Maha: I (1) _____ a report about our {x['subject']} project when you called yesterday.
Hamid: (2) _____ you finished the report yet?
Maha: Yes. Our teacher (3) _____ every detail carefully this morning.
Hamid: You (4) _____ verify the facts before sharing information.
Maha: I agree. If another mistake appears, we (5) _____ correct it immediately."""
  s["grm"]["wordCount"]=W(s["grm"]["passage"])
  s["grm"]["questions"]=[mc(f"Gap {i+1}",opts,0) for i,opts in enumerate([["was preparing","prepare"],["Have","Does"],["checked","checking"],["should","should to"],["will","had"]])]
  s["vcb"]["passage"]=pad(f"""Our school {x['club']} organised a useful project about {x['subject']}. The first (1) _____ described the activity and its meeting time. Students identified their intended (2) _____ and prepared clear information. They collected (3) _____ before publishing the final version. Each important (4) _____ was checked using reliable evidence. This attention to (5) _____ reduced confusion and made the group more responsible. Pupils also learned to cooperate, discuss different views and improve their work.""",70,80)
  s["vcb"]["wordCount"]=W(s["vcb"]["passage"])
  s["vcb"]["questions"]=[mc(f"Gap {i+1}",[a,"journey","bicycle"],0) for i,a in enumerate(["announcement","audience","feedback","message","accuracy"])]
  notices=[
    f"Notice: The {x['club']} will meet in the {x['venue']} on Tuesday to plan {x['project']}. Participants must register before attending. The activity is free and everyone should bring a notebook and follow the teacher's instructions.",
    f"Email: Dear Bilal, I noticed {x['error']} in our first report. We checked {x['evidence']} and corrected it. Please do not share the earlier version before the revised announcement is approved and published.",
    f"School information: Pupils have prepared {x['project']} for visiting families. No fee is required, but everyone should follow the instructions and show respect. Students may ask the organisers questions whenever an explanation is unclear.",
    "Survey: Thirty pupils reviewed the materials. Eighteen preferred the revised explanation, seven wanted more detail and five were uncertain. Organisers planned another session so that everyone could ask questions and offer useful suggestions.",
    f"Coordinator: The final {x['project']} must be checked by {x['expert']} before publication. Errors can be reported privately. Our purpose is accurate information and useful learning, not simply attracting attention on social media."
  ]
  texts=[pad(t,35,45) for t in notices]
  statements=[
    ("Registration is required for the workshop.",True),
    ("Bilal should distribute the incorrect version immediately.",False),
    ("Visitors must pay an admission fee.",False),
    ("Eighteen pupils preferred the revised explanation.",True),
    ("The final project can be published without checking.",False)
  ]
  s["rdg1"]["texts"]=[dict(passage=t,statement=st,answer=0 if truth else 1) for t,(st,truth) in zip(texts,statements)]
  s["rdg1"]["questions"]=[tf(st,truth) for st,truth in statements]
  s["rdg2"]["passage"]=pad(f"""School projects about {x['subject']} can develop valuable skills. Supporters say that producing {x['project']} helps students apply knowledge to practical situations. Members must discuss ideas, plan their responsibilities and think about the people who will benefit. The best outcomes are supported by evidence rather than attractive appearances.

Another benefit is learning how to check information. The {x['club']} can consult {x['expert']} and compare reliable sources. This helps pupils recognise rumours and explains why confident claims are not always correct. Quieter students may contribute through research and careful writing, even when they prefer not to speak in public.

However, practical work can be time-consuming. A first version may contain {x['error']}, and sharing it without checking could confuse visitors. Students must consider privacy and safety. Teachers should supervise unfamiliar equipment and give clear instructions.

Fairness matters as well. Some pupils cannot afford expensive materials or remain at school after lessons. Groups should therefore offer varied roles and use accessible resources. Criticism should be about the evidence and the decisions, not personal disagreements.

In my opinion, responsible school projects are worthwhile when pupils check {x['evidence']}, correct mistakes and invite useful feedback. The strongest result is a class that learns to ask questions, explain uncertainty and improve its work. Responsible judgement is more important than publicity.""",300,350)
  s["rdg2"]["wordCount"]=W(s["rdg2"]["passage"])
  s["rdg2"]["questions"]=[
    mc("What do supporters value?",["Practical skills","Avoiding work","Only gaining fame"],0),
    mc("Who can help check evidence?",["A celebrity",x["expert"],"A football coach"],1),
    mc("What can an uncorrected error cause?",["More prizes","No effect","Confusion for visitors"],2),
    mc("What supports fair participation?",["Affordable materials","Expensive equipment only","No supervision"],0),
    mc("What should criticism focus on?",["Personal insults","Evidence and decisions","Social-media followers"],1),
    mc("What is one disadvantage of projects?",["They need no time","They are always perfect","They require supervision"],2),
    mc("What is the writer's final position?",["Responsible projects are valuable","All projects must be banned","Evidence is unimportant"],0)
  ]
  s["rdg3"]["passage"]=pad(f"""When Aisha joined the {x['club']}, she wanted to learn new skills. The students were preparing {x['project']}. Aisha liked organising research, but she felt nervous about speaking in public. Her friend Mariam explained that a team needs different strengths.

The group met in the {x['venue']} with {x['expert']}. Pupils divided the responsibilities, and Aisha recorded facts and sources. Mariam prepared a small presentation, while two classmates arranged materials. The teacher reminded the group to keep clear notes.

During preparation, Aisha discovered {x['error']}. One student wanted to ignore the problem because the deadline was approaching. Aisha disagreed politely and suggested checking {x['evidence']}. The group examined the source, corrected its explanation and recorded the reason. Everyone appreciated that the improved version was more reliable.

A younger class then tested the project. Some pupils requested simpler language and clearer instructions. Aisha collected their comments and helped rewrite the explanation. She also practised speaking about one section of the work until she felt comfortable answering questions.

On exhibition day, visitors examined the project. One person asked why the group had revised its first version. Aisha explained the original error and the evidence used to correct it. The teacher praised the students for accepting criticism without becoming defensive.

Afterwards, Aisha wrote a reflection. She realised that confidence can grow through preparation, patience and teamwork. Her experience showed that honest decisions matter more than a perfect-looking display.""",350,400)
  s["rdg3"]["wordCount"]=W(s["rdg3"]["passage"])
  s["rdg3"]["questions"]=[
    short("Which club did Aisha join?",x["club"]),
    short("Where did the group meet?",x["venue"]),
    short("What error did Aisha find?",x["error"]),
    short("What evidence did they check?",x["evidence"]),
    mc("Why did Aisha first prefer research?",["She felt nervous speaking","She disliked all pupils","She was absent"],0),
    mc("What did younger pupils request?",["Expensive prizes","Clearer instructions","Longer holidays"],1),
    mc("What did Aisha explain during the exhibition?",["A football game","A shopping trip","Why an error was corrected"],2),
    mc("What did Aisha learn?",["Preparation can build confidence","Quiet students cannot help","Mistakes should be hidden"],0)
  ]
  s["wrt1"]["prompt"]=f"Write an informative text of at least 85 words about how {x['subject']} can benefit students and their community. Include examples and a clear conclusion."
  s["wrt2"]["prompt"]=f"Write a polite email of at least 100 words describing your class {x['project']}. Explain its purpose, a problem you solved, and what you learned."
  assert [s[k]["marks"] for k in ("grm","vcb","rdg1","rdg2","rdg3","wrt1","wrt2")]==[5,5,5,7,8,5,10]
  assert 50<=s["grm"]["wordCount"]<=60
  assert 70<=s["vcb"]["wordCount"]<=80
  name="abcd"[number-1]
  (D/f"unit{number}-paper-{name}.json").write_text(json.dumps(u,ensure_ascii=False,indent=2)+"\n")
  html=ref_html.replace("Those Teenage Things",x["title"]).replace("unit2-",f"unit{number}-").replace("Unit 2",f"Unit {number}").replace("Paper B",f"Paper {name.upper()}").replace("unit2-paper-b.json",f"unit{number}-paper-{name}.json")
  (D/f"paper-{name}-preview.html").write_text(html)
  print(number,x["title"],"60 marks",[(k,W(s[k]["passage"])) for k in ("grm","vcb","rdg2","rdg3")],flush=True)
