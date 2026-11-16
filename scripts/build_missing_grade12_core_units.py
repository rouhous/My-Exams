#!/usr/bin/env python3
"""Draft Grade 12 Core original unit 3/4 nine-section 70-mark exams, by 2026 SAH shape.
Never mark them teacher-certified until detailed book and audio review.
"""
import json,pathlib,copy
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/"grade12/core/units"
base=json.loads((D/"unit2-paper-b.json").read_text(encoding="utf-8"))
view=(D/"paper-b-preview.html").read_text(encoding="utf-8")
units={
3:{"title":"Tourism and Hospitality","topic":"tourism and hospitality","project":"visitor welcome programme","place":"heritage guesthouse","role":"hotel supervisor","problem":"an incorrect booking time","proof":"confirmed reservation","group":"visiting families","feature":"respectful customer service"},
4:{"title":"Travel and Transport","topic":"travel and transport","project":"public transport information guide","place":"transport centre","role":"transport coordinator","problem":"an outdated departure time","proof":"official route timetable","group":"daily passengers","feature":"reliable transport information"}
}
def W(s):return len(s.split())
def extend(s,low,high):
    phrases=[
    "The organisers reminded students that reliable information matters more than a confident voice or an attractive photograph.",
    "They recorded where each statement came from and checked whether the source had changed recently.",
    "Some people needed simple explanations, so the group prepared clear words and invited further questions.",
    "The teacher encouraged everyone to discuss uncertainty honestly rather than present a guess as a fact.",
    "Different students contributed through careful research, writing, practical organisation and respectful discussion with visitors.",
    "After receiving feedback, the group reviewed the first version and noted what had been improved.",
    "Families appreciated the opportunity to understand the choices and learn why a correction had been made.",
    "All the participants were asked to respect other people and follow suitable safety instructions.",
    "The activity also showed how a responsible service needs patience, accuracy and continuing improvement.",
    "Our teacher kept the revised documents so that another class could study the process later.",
    "These habits are valuable in school projects and whenever somebody needs to make an informed decision.",
    "The team compared notes at its final meeting and agreed on practical improvements for the next event.",
    ]
    if high<=45 and W(s)<low:s+=" Please contact the organisers for further information."
    for p in phrases:
      if W(s)>=low:break
      if W(s)+W(p)<=high:s+=" "+p
    if not low<=W(s)<=high:raise ValueError(f"SAH length {W(s)}, expected {low}..{high}")
    return s
def mc(stem,opts,answer):return dict(type="mc",stem=stem,options=opts,answer=answer)
def tf(stem,truth):return dict(type="tf",stem=stem,options=["True","False"],answer=0 if truth else 1)
def short(stem,ans):return dict(type="short",stem=stem,answer=ans,maxWords=4)
for n,x in units.items():
  d=copy.deepcopy(base);d["id"]=f"g12-core-unit{n}-original-paper";d["unit"]={"number":n,"title":x["title"]}
  d["status"]="original_nine_section_teacher_review_draft";d["certifiedTextbookMatch"]=d["readyForStudentExam"]=False
  d["listeningSources"]=[f"unit{n}-listening{i}-original-draft.json" for i in (1,2)]
  s=d["sections"]
  s["grm"]["passage"]=extend(f"""Maha: I (1) _____ the latest {x['topic']} information when you called me yesterday.
Salim: (2) _____ you checked the official details yet?
Maha: Yes. The supervisor (3) _____ the document carefully this morning.
Salim: You (4) _____ tell visitors about any important correction as soon as possible.
Maha: If another mistake appears, I (5) _____ report it to the organisers immediately.""",60,70)
  s["grm"]["wordCount"]=W(s["grm"]["passage"])
  s["grm"]["questions"]=[mc(f"Gap {i+1}",v,0) for i,v in enumerate([["was reading","read now"],["Have","Does"],["checked","checking"],["should","should to"],["will","had"]])]
  s["vcb"]["passage"]=extend(f"""Planning a {x['topic']} activity requires accurate information. The (1) _____ describes arrangements and explains when visitors may arrive. A friendly (2) _____ should listen carefully and respond politely to questions. Staff need to check every (3) _____ before it is confirmed. Clear (4) _____ makes it easier for people to understand the available choices. A respectful attitude improves the overall visitor (5) _____. Students can practise these skills by working together, comparing official sources and correcting inaccurate details before anyone is inconvenienced. Such preparation encourages responsibility and cooperation.""",80,90)
  s["vcb"]["wordCount"]=W(s["vcb"]["passage"])
  s["vcb"]["questions"]=[mc(f"Gap {i+1}",[a,"football","passport"],0) for i,a in enumerate(["schedule","representative","reservation","communication","experience"])]
  notices=[
    f"Visitor notice: The {x['project']} will take place at the {x['place']} on Wednesday afternoon. Participants must register before joining and should arrive ten minutes early. There is no fee for school pupils.",
    f"Email: Dear Salim, we discovered {x['problem']} in our original notice. We checked the {x['proof']} and corrected the information. Please use the new version when contacting visitors and avoid distributing the old message.",
    f"Information desk: Our programme provides simple explanations for {x['group']}. Visitors can ask about accessibility and practical arrangements. The organisers will answer politely and direct people to an appropriate member of staff when they need further assistance.",
    "Survey report: Thirty participants answered questions after the visit. Eighteen found the revised information clearer, seven requested extra detail and five were uncertain. The team agreed to review these comments before preparing another event.",
    f"Coordinator's note: The {x['role']} will check the final announcement before publication. Students should record all changes, especially those affecting safety or schedules. The purpose is trustworthy information rather than collecting followers on social media.",
    "Community message: The event will use reusable materials wherever practical, and participants should leave shared spaces clean. Volunteers are asked to respect local residents, follow safety advice and report any concerns to the organising teacher.",
    f"Reminder: The {x['project']} is designed for learning and will not replace official professional services. Visitors should confirm important arrangements directly with staff and ask questions whenever a detail in the printed information seems unclear."
  ]
  texts=[extend(t,35,45) for t in notices]
  statements=[
    ("Participants must register before attending.",True),
    ("Salim should use the inaccurate notice.",False),
    ("The information desk refuses to answer visitors' questions.",False),
    ("Eighteen participants found the revision clearer.",True),
    ("The final announcement will be published without checking.",False),
    ("Volunteers should keep public spaces clean.",True),
    ("The school activity replaces all professional services.",False),
  ]
  s["rdg1"]["texts"]=[dict(passage=t,statement=st,answer=0 if yes else 1) for t,(st,yes) in zip(texts,statements)]
  s["rdg1"]["questions"]=[tf(st,yes) for st,yes in statements]
  s["rdg2"]["passage"]=extend(f"""Email 1 — From Sara to the visitor information team

Dear Team,

I am preparing a school group visit connected with {x['topic']}. Your website describes {x['project']}, but I would like to confirm the meeting arrangements. Several pupils are travelling from different areas, and one student needs information about accessibility. I would also appreciate advice about what to bring and how much time to allow for the activity.

An earlier message mentioned a different starting time. Could you please confirm which information is current? Our teacher has asked us to verify the details before collecting any payments or arranging transport. Thank you for helping us plan responsibly.

Best wishes,
Sara

Email 2 — From the information team

Dear Sara,

Thank you for your message. We apologise for the confusion caused by {x['problem']}. The current information is recorded in the {x['proof']}, and we have corrected our public notice. The {x['role']} will make sure that staff use the revised version.

The programme will begin at the announced meeting point in the {x['place']}. Please contact us before your visit if any pupil requires additional assistance. We can discuss suitable arrangements and give clear instructions. There is no school participation fee, although families should consider their own travel expenses.

Kind regards,
Information Team

Email 3 — From Sara

Dear Team,

Thank you for checking the details. I appreciate your clear explanation and your willingness to consider different visitors' needs. I will share only the revised information with our group and remind pupils to ask questions respectfully. After the activity, I hope we can send feedback about what we learned.

Best wishes,
Sara""",350,400)
  s["rdg2"]["wordCount"]=W(s["rdg2"]["passage"])
  s["rdg2"]["questions"]=[
    mc("Why does Sara contact the team?",["To confirm visiting arrangements","To complain about a sports match","To order a new phone"],0),
    mc("What information does one pupil need?",["A football timetable","Accessibility arrangements","A shopping voucher"],1),
    mc("What caused confusion?",["A missing photograph","A library closure","Different starting times"],2),
    mc("Who will make sure staff use the corrected version?",["The "+x['role'],"A singer","A tour bus driver"],0),
    mc("Where is the meeting point?",["At a football stadium","At the "+x['place'],"Inside an aircraft"],1),
    mc("What should families consider?",["Only a competition prize","The cost of uniforms","Their own travel expenses"],2),
    mc("How much is the school participation fee?",["There is no fee","Ten rials","Twenty rials"],0),
    mc("What does Sara offer after the visit?",["A public advertisement","Feedback on the experience","A new booking system"],1),
  ]
  s["rdg3"]["passage"]=extend(f"""Reliable {x['topic']} information is important because people make real decisions based on what they read. Visitors may compare prices, travel times, accessibility and safety rules before choosing a service. An attractive advertisement cannot replace a clear explanation of the actual arrangements.

Good organisations prepare accurate public notices and revise them whenever circumstances change. The team managing {x['project']} must check dates and conditions against authoritative sources. A mistake such as {x['problem']} can inconvenience families and damage public trust. When an error is discovered, a responsible organisation should explain the correction openly.

Communication is another essential skill. Staff should listen before answering and avoid assuming that every person has the same needs. Somebody travelling with a child, an older relative or a person with limited mobility may require different practical information. Using simple language and inviting questions helps people understand the service without embarrassment.

Training and teamwork also affect the quality of a visitor's experience. Different staff members may handle bookings, safety checks and information. They need a shared, updated record so that visitors do not receive conflicting answers. A group can practise realistic conversations and review how an unexpected problem should be handled.

Costs and environmental responsibilities deserve attention too. Organisations can reduce unnecessary printing, use durable materials and encourage people to respect shared places. However, environmental claims should be supported by evidence rather than repeated simply because they sound positive. Visitors benefit when choices and limitations are explained honestly.

Students learning about {x['topic']} can develop these habits through small supervised projects. They should compare official information, identify missing details, prepare questions and discuss the possible effects of inaccurate claims. The aim is not to memorise one perfect response. It is to practise responsible judgement, cooperation and clear communication.

Ultimately, {x['feature']} depends on reliable evidence and respect for different people. A service becomes more trustworthy when it welcomes feedback, corrects mistakes promptly and helps visitors make informed choices.""",400,450)
  s["rdg3"]["wordCount"]=W(s["rdg3"]["passage"])
  s["rdg3"]["questions"]=[
    short("Name one factor visitors may compare before choosing a service.","travel times"),
    short("What source should staff use to check changed arrangements?","authoritative sources"),
    short("Name one problem that can inconvenience families.",x["problem"]),
    short("What kind of language helps people understand services?","simple language"),
    short("Name one duty handled by different staff members.","bookings"),
    short("What should support environmental claims?","evidence"),
    mc("What can conflicting information damage?",["Public trust","Only a sports result","A school uniform"],0),
    mc("Why should staff listen carefully?",["Every visitor has identical needs","People have different needs","Questions are not allowed"],1),
    mc("What helps a group respond to unexpected problems?",["Ignoring complaints","Guessing explanations","Training and shared records"],2),
    mc("What is the writer's overall message?",["Evidence and respect are essential","Popularity guarantees accuracy","Corrections should be hidden"],0),
  ]
  s["wrt1"]["prompt"]=f"Write an evaluative essay of at least 100 words discussing the benefits and difficulties of {x['topic']} for local communities. Explain both sides and give your justified opinion."
  s["wrt2"]["prompt"]=f"Write a narrative of at least 100 words beginning: 'We arrived at the meeting point, but the information on our ticket did not match the official notice.' Explain what happened, how the problem was solved and what you learned."
  suffix="c" if n==3 else "d"
  (D/f"unit{n}-paper-{suffix}.json").write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  html=view.replace("Starting University",x["title"]).replace("unit2-",f"unit{n}-").replace("Unit 2",f"Unit {n}").replace("Paper B",f"Paper {suffix.upper()}").replace("unit2-paper-b.json",f"unit{n}-paper-{suffix}.json")
  html=html.replace(f"unit{n}-paper-b.json",f"unit{n}-paper-{suffix}.json")
  (D/f"paper-{suffix}-preview.html").write_text(html,encoding="utf-8")
  assert sum(part['marks'] for part in s.values())+15==70
  print(f"Grade 12 Core Unit {n} {x['title']}: 70 marks, 9 sections",[(k,W(s[k]['passage'])) for k in ("grm","vcb","rdg2","rdg3")],flush=True)
