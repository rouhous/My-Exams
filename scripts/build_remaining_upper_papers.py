#!/usr/bin/env python3
"""Create original, unit-specific teacher-review EXAM DRAFTS from 8 independently authored scenario cards.
All units have the September 2026 SAH section counts and marks. No card is certified to textbook pages.
NEVER recycle an older examination under a different unit title.
"""
import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROFILES=json.loads((ROOT/"targeted_units/upper_remaining_profiles.json").read_text())["profiles"]
DEST=ROOT/"targeted_units/full_papers.json"
def words(s):return len(s.split())
def mc(stem,answer,wrong1,wrong2,i=0,kind=None):
    opts=[answer,wrong1,wrong2]; n=i%3
    opts=opts[n:]+opts[:n]; return dict(type="mc",stem=stem,options=opts,answer=opts.index(answer),**({"kind":kind} if kind else {}))
def tf(stem,yes):return dict(type="tf",stem=stem,options=["True","False"],answer=0 if yes else 1)
def short(stem,ans):return dict(type="short",stem=stem,answer=ans,maxWords=8)
def extras(p):
    return [
      f"The participants returned to {p['setting']} with clearer questions and a better understanding of the original challenge.",
      f"At every stage, the students checked {p['evidence']} before making a public claim about the results.",
      f"Several family members said that {p['future']} would make the project useful beyond the first event.",
      f"Teachers encouraged the group to discuss {p['counterpoint']} and respect people whose priorities were different.",
      f"The class also considered {p['ethic']} as an important example of responsible communication.",
      f"A visitor asked why {p['lesson']} should matter to younger students preparing for unfamiliar situations.",
      f"Volunteers used {p['material']} to demonstrate the difference between the original plan and its improved version.",
      f"Before publishing information, the pupils asked {p['guest']} to check the accuracy of their explanation.",
      f"The organisers made a record of questions that could not be answered confidently during the first session.",
      f"Later feedback suggested that clear evidence was more persuasive than an impressive but unsupported statement.",
      f"Each group member had a chance to describe their own experience without being interrupted or judged.",
      f"The project encouraged students to compare possible solutions instead of assuming the first idea would succeed."
    ]
def fit(s,lo,hi,p,kind):
    # Only add relevant, nonduplicated, source-anchored editorial sentences.
    if words(s)>hi:
        # Remove complete final untested sentences, never truncate in the middle of a word.
        while words(s)>hi:
            z=re.search(r"\s+[^.!?\n]+[.!?]\s*$",s)
            if not z:break
            s=s[:z.start()].rstrip()
    if words(s)<lo:
        for a in extras(p):
            if words(s)>=lo:break
            if words(s)+words(a)<=hi:
                if kind=="dialogue":
                    lines=s.splitlines()
                    lines[-1]+=" "+a
                    s="\n".join(lines)
                else:s=s.rstrip()+" "+a
    if words(s)<lo:
        for a in ("The teacher welcomed questions.", "Students compared their answers.", "The team kept careful notes.", "This helped everyone understand.", "The decision was checked again.", "Useful feedback followed the activity."):
            if words(s)>=lo:break
            if words(s)+words(a)<=hi:
                if kind=="dialogue":
                    lines=s.splitlines();lines[-1]+=" "+a;s="\n".join(lines)
                else:s=s.rstrip()+" "+a
    if not lo<=words(s)<=hi:raise ValueError(f"{p['grade']}-{p['track']}-{p['unit']} {kind} {words(s)} not {lo}-{hi}")
    return s
def dialogue(p,kind):
    fields=[
     ("What activity is your group preparing?",f"Our project is {p['topic']}, which we are organising at {p['setting']}. We want useful results."),
     ("Who is responsible for helping the young volunteers?",f"{p['leader']} is leading the work and explaining how everyone can contribute."),
     ("When will the main event take place?",f"It is arranged for {p['occasion']}, after the timetable has been checked."),
     ("How many people are participating?",f"We have {p['participants']}, who have different roles in the team."),
     ("What made the project necessary?",f"The main problem was that {p['challenge']}. We wanted to investigate instead of guessing."),
     ("What information helped you understand the problem?",f"We examined {p['evidence']}. This was more useful than repeating rumours."),
     ("What practical action did you finally choose?",f"The agreed plan was {p['solution']}. We wrote down clear steps."),
     ("What change did you notice after the activity?",f"We observed that {p['result']}. The team collected written feedback."),
     ("What do you hope to do next term?",f"We hope to develop {p['future']}, once the plans have been approved."),
     ("How did you protect the people involved?",f"We followed the rule of {p['ethic']}. It was essential throughout."),
     ("Was everybody in agreement?",f"Not quite. Some visitors argued that {p['counterpoint']}. Their opinions were recorded."),
     ("Who gave the students advice from outside school?",f"We invited {p['guest']}, whose suggestions made our discussions more practical."),
     ("Which equipment did you use for the demonstration?",f"We worked with {p['material']}. Everyone followed the safety instructions."),
     ("What lesson would you share with our listeners?",f"We learnt that {p['lesson']}. That idea will guide future decisions.")
    ]
    if kind=="11-core":
        fields=[(q.replace(" is your group"," are you").replace(" do you hope"," will you"),a.split(". ")[0]+".") for q,a in fields]
    elif kind=="11-elective":
        fields=[(q+" Could you give a clear example?",a+" We discussed it carefully with our classmates.") if i%3==0 else (q,a) for i,(q,a) in enumerate(fields)]
    lines=[]
    for q,a in fields:lines.extend(["Interviewer: "+q,"Student: "+a])
    ranges={"11-core":(300,350),"11-elective":(400,450),"12-core":(350,450)}
    s=fit("\n".join(lines),*ranges[kind],p,"dialogue")
    assert 25<=len(s.splitlines())<=30
    return s
def narrative(p,kind):
    paragraphs=[
     f"My name is {p['storyPerson']}. Our class had been learning about {p['title']} when a practical problem changed how I understood the subject. We were exploring {p['topic']} and had planned to meet at {p['setting']}. I was pleased to join because I wanted to practise communicating with people whose experiences were different from mine.",
     f"The challenge began when {p['storyIssue']}. I did not want to make a quick judgement, particularly because an incorrect assumption could affect other people. I told {p['leader']} what had happened and asked how to check the available information. We agreed that finding the cause was more important than looking for somebody to blame.",
     f"After listening to different suggestions, {p['storyAction']}. We used {p['material']} and compared our first impression with {p['evidence']}. The group also spoke to {p['guest']} for a second opinion. That conversation showed me why a confident explanation is not always a reliable explanation.",
     f"Several pupils were unsure whether our approach would work. Their concern was understandable because {p['counterpoint']}. We considered those doubts and checked which steps were practical. I learnt that listening respectfully to an alternative view can strengthen a plan rather than delay it.",
     f"Eventually, {p['storyOutcome']}. We reported the result to the people who had helped us and invited feedback. The discussion included {p['ethic']}, because completing a successful project should never mean ignoring another person's rights or safety.",
     f"Looking back, I believe {p['lesson']}. The experience has changed the way I approach group work. We are now hoping to prepare {p['future']}, but first we will review the evidence again. I feel more able to ask questions and make careful decisions in an unfamiliar situation."
    ]
    if kind in ("11-core","12-core"):
        s="Part One\n\n"+"\n\n".join(paragraphs[:3])+"\n\nPart Two\n\n"+"\n\n".join(paragraphs[3:])
    else:s="\n\n".join(paragraphs)
    ranges={"11-core":(350,400),"11-elective":(400,450),"12-core":(350,450)}
    return fit(s,*ranges[kind],p,"narrative")
def evaluative(p,kind):
    para=[
     f"Many schools are discussing whether {p['debate'].lower()}. Supporters argue that {p['pro']}. These benefits are worth taking seriously because they address problems encountered by real students and families. A carefully planned project can show how classroom learning is useful beyond an examination.",
     f"Another argument in favour is the opportunity to cooperate with people who have different experience. At {p['setting']}, young volunteers listened to {p['guest']} and explored {p['topic']}. They discovered that a decision becomes clearer when examples and evidence support a claim.",
     f"However, critics note that {p['con']}. Schools have limited resources and cannot introduce every new idea without considering costs and other priorities. A programme that works well in one setting may not suit everyone, especially when local circumstances are different.",
     f"The evidence also deserves attention. Our scenario included {p['evidence']}, which made it possible to test the assumptions of both supporters and critics. Yet this kind of information has limits. A single project cannot guarantee that the same result will follow in another place.",
     f"A sensible compromise is to test an approach on a small scale, gather feedback and revise the plan. The students proposed {p['solution']} rather than claiming that every concern had disappeared. They also considered {p['ethic']} and encouraged respectful questions.",
     f"In my view, the strongest decision is one that weighs benefits and drawbacks carefully. I support practical experiments when they are transparent and inclusive, but I would not accept a promise of guaranteed success. The larger lesson is that {p['lesson']}."
    ]
    if kind=="11-core":para=[x.split(". ")[0]+". "+(x.split(". ")[1] if len(x.split(". "))>1 else "") for x in para[:5]]+[para[-1]]
    s="\n\n".join(para)
    return fit(s,*( (300,350) if kind=="11-core" else (400,450)),p,"evaluative")
def informative(p):
    heads=["The purpose and the people","Finding the original challenge","Using evidence carefully","Testing a proposed change","Listening to different views","Lessons for the future"]
    para=[
     f"Paragraph A\nThe project called {p['topic']} was introduced at {p['setting']}. It was supported by {p['leader']} and involved {p['participants']}. The aim was to connect classroom ideas with a practical question. Students identified tasks for volunteers and agreed to communicate any change through a reliable channel.",
     f"Paragraph B\nThe group noticed that {p['challenge']}. This was important because the issue affected more than the students directly involved. Instead of blaming individuals, the organisers gathered questions from participants and considered what had happened before the event. They made sure that concerns were recorded accurately.",
     f"Paragraph C\nUseful research depended on {p['evidence']}. Students compared this material with interviews and observations. They checked dates, asked whether a source could be trusted and distinguished measured facts from personal opinions. {p['guest'].capitalize()} offered advice but did not replace the team's own responsibility to examine evidence.",
     f"Paragraph D\nAfter discussing several possibilities, participants agreed on {p['solution']}. They used {p['material']} for a supervised demonstration and checked whether the approach was practical. The first trial was treated as an opportunity to learn, not as proof that every aspect of the project was perfect.",
     f"Paragraph E\nNot all responses were identical. Some participants argued that {p['counterpoint']}. The organisers recognised the concern and listened without interrupting. They also emphasised {p['ethic']}, which mattered even when a faster or cheaper option appeared attractive.",
     f"Paragraph F\nThe final report found that {p['result']}. Volunteers suggested a next stage involving {p['future']}. The project showed the value of checking information, explaining decisions clearly and inviting feedback. It also demonstrated that {p['lesson']}, a principle that applies to many situations beyond the original setting."
    ]
    return fit("\n\n".join(para),400,450,p,"informative"),heads
def emails(p):
    txt=f"""Email 1 — From {p['storyPerson']} to the organiser

Dear Organiser,

I am writing about {p['topic']}. Our class is interested in the event at {p['setting']}, but I have a few questions before we take part. The main difficulty we have heard about is that {p['challenge']}. Could you explain what arrangements are being made and whether students can ask questions during the session?

Several members of our group would like to understand how {p['material']} will be used. We are also concerned about {p['ethic']}. I would appreciate a clear answer so that the information can be shared accurately.

Kind regards,
{p['storyPerson']}

Email 2 — From the organiser to {p['storyPerson']}

Dear {p['storyPerson']},

Thank you for your thoughtful email. The event is scheduled for {p['occasion']}, and {p['leader']} will explain the programme before any activity begins. We investigated {p['evidence']} and agreed on {p['solution']}. We believe this responds to the main problem, although we welcome further suggestions.

We understand that {p['counterpoint']}. A separate information desk will allow visitors to ask about alternatives. {p['guest'].capitalize()} will also be available to discuss practical details.

Yours sincerely,
The Organising Team

Email 3 — From {p['storyPerson']} to the organiser

Dear Team,

Thank you for the detailed reply. I have shared your explanation with the class, and the students are pleased that their concerns were considered. We will arrive on time and bring the materials requested by our teacher.

I am especially interested to see whether {p['result']}. We hope to take part in {p['future']} later in the term. I agree that {p['lesson']}. Please let us know if any arrangements change before the event.

Best wishes,
{p['storyPerson']}"""
    return fit(txt,350,400,p,"emails")
def short_texts(p,n):
    themes=[
       (f"The organisers announced {p['topic']} at {p['setting']}. Students were asked to check the latest programme before travelling and to contact the coordinator with questions. The event was scheduled for {p['occasion']}, and visitors would receive an introduction before the activity began.","The event was scheduled for "+p["occasion"]+".",True),
       (f"{p['leader'].capitalize()} invited volunteers to investigate a practical issue. The original concern was that {p['challenge']}. The team recorded observations and asked members to check uncertain claims before suggesting a solution. Nobody was required to publish personal information during the investigation.","The team ignored the original problem instead of investigating it.",False),
       (f"Students collected {p['evidence']} as part of a school project. They then compared the information with advice from {p['guest']}. The group wanted a reliable explanation, so they corrected unclear labels before sharing its conclusions with families and younger pupils.","The group consulted an outside guest before publishing conclusions.",True),
       (f"A notice explained that {p['solution']}. It also warned that a successful trial does not guarantee the same result everywhere. Participants could make suggestions anonymously and were encouraged to ask for further information rather than accept an uncertain statement.","The notice guaranteed that the method would succeed in every setting.",False),
       (f"Several visitors commented that {p['counterpoint']}. The teacher asked the class to listen respectfully and record those opinions. The students agreed that fairness required considering different needs, even when one idea seemed easier to organise or less expensive.","All visitors agreed with the first proposal.",False),
       (f"The follow-up report found that {p['result']}. It recommended {p['future']} as a possible next stage. The project leaders said the suggestion still needed planning and review before it could be offered to another class or school.","The next stage required further planning and review.",True),
       (f"All team members were reminded about {p['ethic']}. The school considered this a necessary responsibility rather than an optional activity. People who had questions were invited to speak to the organiser privately, and the final summary avoided revealing personal details.","The school considered the responsibility described in the notice optional.",False)
    ]
    out=[]
    for text,statement,truth in themes[:n]:
       text=fit(text,35,45,p,"short-text")
       out.append(dict(passage=text,statement=statement,answer=0 if truth else 1))
    return out
def grammar(p,kind):
    # Five item dialogue cloze. Correct forms are unit-specific, with only two alternatives.
    key=(p["grade"],p["unit"])
    forms={
     (11,1):[("usually share","usually shares"),("are preparing","prepare yesterday"),("should check","should checking"),("was sent","were sending"),("have completed","has completed")],
     (11,3):[("are travelling","travels yesterday"),("will visit","visiting"),("are going to meet","going meet"),("should respect","should respecting"),("were guided","was guiding")],
     (11,4):[("was designed","designed was"),("have tested","has tested"),("were improved","was improved"),("is being checked","checks yesterday"),("will present","presented yesterday")],
     (12,2):[("had checked","has checking"),("had completed","have completing"),("was studying","study yesterday"),("had arrived","has arrive"),("would ask","will asked")],
     (12,3):[("will explain","explains tomorrow if"),("arrive","will arrive"),("will change","changed"),("asks","ask to"),("will provide","providing")],
     (12,4):[("have used","has used"),("since","for"),("for","since"),("has been waiting","have been waiting"),("have travelled","has travelled")]
    }
    raw=forms.get(key,forms[(11,1)])
    cases=[
     "Teacher: We (1) ____ clear messages about the programme before school events begin.",
     "Pupil: Our group (2) ____ a short report about the recent project this week.",
     "Teacher: Everyone (3) ____ information before sharing an uncertain claim with families.",
     "Pupil: The first notice (4) ____ during a busy session, so we reviewed it.",
     "Teacher: The team (5) ____ its next decision after discussing the feedback carefully."
    ]
    # For tense-specific 12C, sentences are generated with unambiguous temporal signals.
    if key==(12,2):
       cases=["Student: Before the first lecture, I (1) ____ the new timetable.",
       "Friend: By Monday, she (2) ____ the accommodation application.",
       "Student: At six yesterday, I (3) ____ in the library.",
       "Friend: The adviser (4) ____ before the visitors entered.",
       "Student: She said she (5) ____ for help if necessary."]
    if key==(12,3):
       cases=["Guide: If visitors ask about the programme, I (1) ____ it clearly.",
       "Guest: If we (2) ____ early, can we explore the market?",
       "Guide: If heavy rain starts, the team (3) ____ the route.",
       "Guest: If a visitor (4) ____ about accessibility, please answer.",
       "Guide: If the tour is delayed, we (5) ____ an alternative."]
    if key==(12,4):
       cases=["Passenger: We (1) ____ this bus route for several years.",
       "Driver: The new timetable has been available (2) ____ September.",
       "Passenger: I have waited here (3) ____ twenty minutes.",
       "Driver: The bus (4) ____ for the traffic to clear.",
       "Passenger: Many families (5) ____ by bus rather than car."]
    txt="\n".join(cases)
    lo,hi=(50,60) if p["grade"]==11 else (60,70)
    txt=fit(txt,lo,hi,p,"grammar")
    qs=[dict(type="mc",stem=f"Gap {i+1}",options=[good,bad],answer=0) for i,(good,bad) in enumerate(raw)]
    return dict(title="Grammar dialogue cloze",marks=5,passage=txt,wordCount=words(txt),questions=qs)
def vocabulary(p,kind):
    terms=p["vocab"]
    sentences=[
     f"Our project about {p['title']} introduced several useful English expressions to the class.",
     f"The first word, (1) _____, was associated with {p['topic']}.",
     f"We used (2) _____ when explaining {p['challenge']} to visitors.",
     f"A third important expression, (3) _____, helped describe {p['solution']}.",
     f"During the demonstration, the meaning of (4) _____ became easier to understand.",
     f"Finally, we discussed (5) _____ in relation to {p['future']}.",
     "Students checked each word in context, asked questions and prepared short examples for younger learners."
    ]
    txt=" ".join(sentences)
    lo,hi=(70,80) if p["grade"]==11 else (80,90)
    txt=fit(txt,lo,hi,p,"vocabulary")
    allwords=terms[:]
    qs=[]
    for i,x in enumerate(terms):
       wrong=terms[(i+1)%5];wrong2=terms[(i+3)%5]
       qs.append(mc("Gap "+str(i+1),x,wrong,wrong2,i))
    return dict(title="Vocabulary cloze",marks=5,passage=txt,wordCount=words(txt),questions=qs)
def build(p):
    kind=str(p["grade"])+"-"+p["track"]
    l1=dialogue(p,kind);l2=narrative(p,kind)
    id=f"{kind}-unit{p['unit']}"
    m1=[mc("Where did the project take place?",p["setting"],"At an airport","In a different country",i=0),
        mc("Who coordinated the project?",p["leader"],"A popular singer","A television presenter",i=1),
        mc("When was the main event organised?",p["occasion"],"Friday midnight","Sunday evening",i=2),
        mc("How many volunteers were involved?",p["participants"],"Two volunteers","Two hundred volunteers",i=0),
        mc("What problem did the students investigate?",p["challenge"],"An unrelated sports match","A school uniform competition",i=1),
        mc("What did the group propose?",p["solution"],"Ignore all feedback","Cancel every school event",i=2)]
    if kind=="11-elective":
       ql1=m1+[tf("The team examined evidence before reaching a decision.",True),tf("The group ignored every alternative opinion.",False),tf("Respect for people was part of the planning.",True),tf("The organisers claimed no future improvements were needed.",False)]
       ql2=[short("Who is telling the story?",p["storyPerson"]),short("Who guided the investigation?",p["leader"]),short("Who offered a second opinion?",p["guest"]),short("Where did the team share its report?",p["setting"]),short("What difficulty first occurred?",p["storyIssue"]),short("What outcome was described?",p["storyOutcome"])]
       # Four fill-in answers are explicitly spoken in the source's topic terms.
       spoken="The four key terms we discussed were "+", ".join(p["keywords"])+" and these ideas helped our project."
       l2=fit(l2+" "+spoken,400,450,p,"narrative")
       ql2 += [dict(type="gap",stem=f"Complete one important unit word ({i+1}).",answer=word,maxWords=2) for i,word in enumerate(p["keywords"])]
    else:
       ql1=m1+[mc("What is the group's next plan?",p["future"],"Stop learning","Hide the report",i=0)]
       ql2=[short("Who narrates this experience?",p["storyPerson"]),short("Who offered advice?",p["leader"]),short("Where was the report presented?",p["setting"]),short("What is planned next?",p["future"]),
       mc("What caused the first problem?",p["storyIssue"],"A football match","A shopping discount",i=0),
       mc("What action did the narrator take?",p["storyAction"],"Ignored the evidence","Blamed the whole class",i=1),
       mc("What happened after the investigation?",p["storyOutcome"],"The project was abandoned","The students hid the result",i=2),
       mc("What was the main lesson?",p["lesson"],"Planning is never useful","Students must never ask questions",i=0)]
    secs={"lst1":dict(title="Listening 1",marks=10 if kind=="11-elective" else 7,script=l1,wordCount=words(l1),speakerTurns=28,speakers=["Interviewer","Student"],questions=ql1,sourceUnit=p["unit"],audio=None),
          "lst2":dict(title="Listening 2",marks=10 if kind=="11-elective" else 8,script=l2,wordCount=words(l2),questions=ql2,sourceUnit=p["unit"],audio=None)}
    ev=evaluative(p,kind)
    info,headings=informative(p)
    if kind=="11-elective":
       qs1=[short("Which benefit do supporters identify?",p["vocab"][0]),short("Who offered an outside perspective?",p["guest"]),short("What evidence did students examine?",p["evidence"]),short("What concern did critics raise?",p["con"]),short("What solution was suggested?",p["solution"]),short("What is the writer's main lesson?",p["lesson"])]
       qs1 += [tf("The writer thinks benefits and drawbacks should both be considered.",True),tf("The text claims no resources are needed for new projects.",False),tf("The project involved examining evidence.",True),tf("The writer says all decisions must be made without feedback.",False)]
       headings=[f"Introducing {p['title']}","Recognising the original problem","Examining the evidence","Testing a possible solution","Handling different opinions","Looking to the future","The world's tallest building"]
       qs2=[
       mc("The word practical in paragraph D is closest to ____.", "useful","imaginary","dangerous",i=0,kind="meaning"),
       mc("The word reliable in paragraph C most nearly means ____.", "trustworthy","confusing","unusual",i=1,kind="meaning"),
       mc("What was the aim of the school project?",p["topic"],"Compete in a sports match","Plan a private party",i=2),
       mc("What did the students use as evidence?",p["evidence"],"Only unsupported rumours","An unrelated television script",i=0),
       mc("Who offered outside advice?",p["guest"],"A famous singer","A football referee",i=1),
       mc("What happened at the final stage?",p["result"],"All work stopped","Every question was ignored",i=2)]
       qs2 += [dict(type="match",stem=f"Match Paragraph {letter} to its heading.",options=headings,answer=i) for i,letter in enumerate("ABCD")]
       secs["rdg1"]=dict(title="Reading 1: Evaluative",marks=10,passage=ev,wordCount=words(ev),questions=qs1)
       secs["rdg2"]=dict(title="Reading 2: Informative",marks=10,passage=info,wordCount=words(info),paragraphs=6,headings=headings,questions=qs2)
       values=p["chart"];secs["wrt1"]=dict(title="Writing 1: Describe data",marks=10,minWords=100,prompt=f"Describe the change shown in the four-week chart for {p['topic']}. Compare figures, explain the overall trend, and include all four values. Write at least 100 words.",chart=dict(title=p["title"]+" participation",categories=["Week 1","Week 2","Week 3","Week 4"],series=[dict(name="Participants",values=values)]))
       secs["wrt2"]=dict(title="Writing 2: Formal email",marks=10,minWords=100,prompt=f"Write a formal email to your school principal proposing {p['future']}. Explain the purpose, the preparations needed and how the proposal relates to {p['title']}. Write at least 100 words.")
    else:
       secs["grm"]=grammar(p,kind);secs["vcb"]=vocabulary(p,kind)
       rdg1=short_texts(p,5 if kind=="11-core" else 7)
       secs["rdg1"]=dict(title="Reading 1: Short text true/false",marks=len(rdg1),texts=rdg1,questions=[tf(t["statement"],t["answer"]==0) for t in rdg1])
       if kind=="11-core":
          q2=[
           mc("What is the main issue discussed by the writer?",p["debate"],"An unrelated sports story","A journey to another continent",0),
           mc("What is one benefit of the proposal?",p["pro"],"It removes every choice","It prevents questions",1),
           mc("What is the main concern raised by critics?",p["con"],"No concern is mentioned","It always saves money",2),
           mc("What evidence did pupils consider?",p["evidence"],"Celebrity gossip","Football scores",0),
           mc("What response did students suggest?",p["solution"],"Ignore the problem","Stop the project",1),
           mc("What does the writer recommend?",p["lesson"],"Avoid checking evidence","Make every decision alone",2),
           mc("What type of argument is the passage?", "balanced and evaluative","only narrative","an advertisement",0)]
          secs["rdg2"]=dict(title="Reading 2: Evaluative",marks=7,passage=ev,wordCount=words(ev),questions=q2)
          narr=fit(narrative(p,kind).replace("Part One\n\n","").replace("\n\nPart Two\n\n","\n\n"),350,400,p,"reading-narrative")
          q3=[short("Who is the main character?",p["storyPerson"]),short("Who helped the student?",p["leader"]),short("What problem did they face?",p["storyIssue"]),short("Where did they share the result?",p["setting"]),
           mc("What did the character do?",p["storyAction"],"Ignored the facts","Left the project",0),
           mc("What was the outcome?",p["storyOutcome"],"Nothing changed","Everyone gave up",1),
           mc("Who offered advice?",p["guest"],"A famous singer","An anonymous actor",2),
           mc("Which message best suits the story?",p["lesson"],"Evidence never matters","Never ask for advice",0)]
          secs["rdg3"]=dict(title="Reading 3: Narrative",marks=8,passage=narr,wordCount=words(narr),questions=q3)
          secs["wrt1"]=dict(title="Writing 1: Informative",marks=5,minWords=85,prompt=f"Write an informative text of at least 85 words explaining {p['topic']}. Include a practical example, two useful suggestions and a clear conclusion.")
          secs["wrt2"]=dict(title="Writing 2: Interactive email",marks=10,minWords=100,prompt=f"Your friend emails: 'I am interested in {p['title']}, but I do not know how to start a school project.' Write a friendly reply of at least 100 words, suggest steps, explain how to get help and respond to your friend's concerns.")
       else:
          email=emails(p)
          qs2=[mc("Who sent the first email?",p["storyPerson"],"A shop manager","An unknown tourist",0),
           mc("What was the subject of the exchange?",p["topic"],"Football results","A music festival",1),
           mc("Where will the event take place?",p["setting"],"At an airport","In a museum abroad",2),
           mc("Who will coordinate it?",p["leader"],"A film director","A famous singer",0),
           mc("What solution was given?",p["solution"],"The project was cancelled","No action was taken",1),
           mc("Who was available to offer advice?",p["guest"],"A sports referee","A shop cashier",2),
           mc("When was the event arranged?",p["occasion"],"Friday midnight","Sunday evening",0),
           mc("What follow-up did the sender mention?",p["future"],"Closing the school","Ignoring the reply",1)]
          secs["rdg2"]=dict(title="Reading 2: Interactive emails",marks=8,passage=email,wordCount=words(email),questions=qs2)
          qs3=[short("Where was the project introduced?",p["setting"]),short("Who led the work?",p["leader"]),short("What information was collected?",p["evidence"]),short("Who offered advice?",p["guest"]),short("What was the proposed response?",p["solution"]),short("What future work was suggested?",p["future"]),
          mc("What problem was investigated?",p["challenge"],"An unrelated story","A missing sports trophy",0),
          mc("Which statement best describes the team?", "It considered evidence and concerns","It refused to listen","It worked without information",1),
          mc("What did the organisers emphasise?",p["ethic"],"Only speed","Only appearance",2),
          mc("What was the main outcome?",p["result"],"The event did not happen","The group lost every record",0)]
          secs["rdg3"]=dict(title="Reading 3: Informative",marks=10,passage=info,wordCount=words(info),questions=qs3)
          secs["wrt1"]=dict(title="Writing 1: Evaluative",marks=10,minWords=100,prompt=f"Evaluate this statement: {p['debate']}. Discuss two advantages and two possible disadvantages with examples from {p['title']}, then give your opinion. Write at least 100 words.")
          secs["wrt2"]=dict(title="Writing 2: Narrative",marks=10,minWords=100,prompt=f"Write a story beginning: '{p['storyPerson']} arrived at {p['setting']} and immediately realised that something had changed.' Explain the problem, how the characters responded and what happened in the end. Write at least 100 words.")
    order=[x["id"] for x in SPEC["tracks"][kind]["sections"]]
    assert set(order)==set(secs.keys()),(kind,order,secs.keys())
    total=sum(secs[x]["marks"] for x in order)
    assert total==SPEC["tracks"][kind]["marks"],(kind,total)
    for k in ("lst1","lst2"):
       official=next(z for z in SPEC["tracks"][kind]["sections"] if z["id"]==k)
       lo,hi=official["lengthWords"]
       assert lo<=secs[k]["wordCount"]<=hi,(kind,p["unit"],k,secs[k]["wordCount"])
    return dict(id=id,grade=p["grade"],track=p["track"],unit=p["unit"],unitTitle=p["title"],model=p["model"],
       marks=total,minutes=SPEC["tracks"][kind]["minutes"],sectionOrder=order,sections=secs,
       status="original_unit_focused_teacher_review_draft_not_officially_approved",
       certifiedTextbookMatch=False,readyForStudentExam=False,reference="UPPER_GRADES_SAH_SEM1_2026_SPEC.json")
SPEC=json.loads((ROOT/"UPPER_GRADES_SAH_SEM1_2026_SPEC.json").read_text())
def main():
    papers=[build(p) for p in PROFILES]
    assert len(papers)==8 and len({x["id"] for x in papers})==8
    output=dict(version="original-unit-rebuild-2026-11-14-v1",scope="only missing Grade 11/12 unit drafts",teacherReviewRequired=True,
        modelCount=len(papers),papers=papers)
    DEST.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n")
    for p in papers:print("DRAFT",p["id"],p["marks"],"sections",len(p["sections"]),"source words", {k:len(v.get("script","").split()) for k,v in p["sections"].items() if k.startswith("lst")})
if __name__=="__main__":main()
