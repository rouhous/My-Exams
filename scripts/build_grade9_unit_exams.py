#!/usr/bin/env python3
"""Build original 7-task Grade 9 unit-specific exams from checked source data."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"grade9/unit-exams"
source=json.loads((OUT/"source-content.json").read_text())
skills=json.loads((ROOT/"grade9/unit-remediation/units.json").read_text())
CLOZES=json.loads("{\"1\":{\"passage\":\"Every autumn, our school (1) _____ an identity week. My friend Huda usually (2) _____ family stories with her grandmother, but this month she (3) _____ a photo board about her interests. Her classmates (4) _____ helping her choose captions in Arabic and English. Huda is sometimes shy, yet she becomes (5) _____ when she describes her favourite subjects. She (6) _____ learning about other people's traditions and never (7) _____ a new pupil by appearance alone. Today she (8) _____ her classmates about their hobbies, and she always (9) _____ the answers carefully. She is particularly interested (10) _____ the different skills that help people work together.\",\"questions\":[[[\"holds\",\"hold\",\"holding\"],0],[[\"share\",\"shares\",\"shared\"],1],[[\"created\",\"creates\",\"is creating\"],2],[[\"are\",\"is\",\"be\"],0],[[\"confidence\",\"confident\",\"confidently\"],1],[[\"enjoy\",\"enjoyed\",\"enjoys\"],2],[[\"judges\",\"judging\",\"judge\"],0],[[\"interview\",\"interviews\",\"is interviewing\"],2],[[\"remembering\",\"remembers\",\"remember\"],1],[[\"at\",\"on\",\"in\"],2]]},\"2\":{\"passage\":\"Last month, our class (1) _____ a short film about different ways of communicating. While we (2) _____ older relatives, one student (3) _____ an unfamiliar expression in the recording. We asked the speaker (4) _____ explain its meaning rather than guessing. The grandparents enjoyed (5) _____ about the messages they had sent in the past. When the microphone (6) _____ working, we checked its batteries and (7) _____ the question. Our teacher reminded us to listen (8) _____ every answer carefully and to speak (9) _____ visitors politely. By the end of the project, we (10) _____ several words that younger pupils had not known before.\",\"questions\":[[[\"made\",\"make\",\"were making tomorrow\"],0],[[\"interview\",\"were interviewing\",\"are interviewing\"],1],[[\"notices\",\"was noticing now\",\"noticed\"],2],[[\"to\",\"for\",\"at\"],0],[[\"talked\",\"talking\",\"talk\"],1],[[\"stops\",\"is stopping\",\"stopped\"],2],[[\"repeated\",\"repeat\",\"repeating\"],0],[[\"at\",\"to\",\"about\"],1],[[\"in\",\"on\",\"to\"],2],[[\"had learned\",\"learning\",\"learns\"],0]]},\"3\":{\"passage\":\"Our science club (1) _____ a smart-home exhibition next month. We have already agreed on the plan, and we (2) _____ an engineer on Wednesday to check the prototypes. The official programme (3) _____ at nine o'clock on Thursday morning. I think more families (4) _____ use helpful technology in the future, but a device should not make every decision for people. Look at the new soil sensor; its warning light is flashing, so it (5) _____ need checking. If a test fails, we (6) _____ the measurements before making changes. Why don't we (7) _____ a clearer guide? The group is going to (8) _____ the software after collecting feedback. We must remember to (9) _____ off equipment safely and (10) _____ up unfamiliar technical words before presenting them.\",\"questions\":[[[\"are going to hold\",\"held yesterday\",\"is hold\"],0],[[\"met last week\",\"are meeting\",\"meet yesterday\"],1],[[\"is started\",\"starting yesterday\",\"starts\"],2],[[\"will\",\"would have\",\"were\"],0],[[\"going to\",\"is going to\",\"is going\"],1],[[\"checking\",\"checked yesterday\",\"will check\"],2],[[\"design\",\"designing\",\"designed\"],0],[[\"improving\",\"improve\",\"improved\"],1],[[\"turning\",\"turned\",\"turn\"],2],[[\"look\",\"looking\",\"looked\"],0]]}}")
def choice(stem,opts,ans):
    return {"stem":stem,"choices":opts,"answer":ans}
models=[]
for unit in source["units"]:
    i=unit["unit"]
    practice=skills["units"][i-1]
    assert practice["title"].casefold()==unit["title"].casefold()
    imageItems=[]
    for j,text in enumerate(unit["listening1"],1):
        g=source["imageGroups"][text["group"]]
        assert len(g["imgs"])==3 and len(text["script"].split())>=40
        imageItems.append(dict(stem=text["stem"],choices=g["labels"],
            images=["../images/"+f for f in g["imgs"]],answer=text["answer"],
            script=text["script"]))
    interview="\n".join(role+": "+text for role,text in unit["interview"])
    interviewItems=[choice(stem,opts,ans) for stem,opts,ans in unit["interviewQs"]]
    cloze=CLOZES[str(i)]
    gvItems=[choice("Gap "+str(j+1),pair[0],pair[1]) for j,pair in enumerate(cloze["questions"])]
    gvText=cloze["passage"]
    reading1=[choice("Person "+str(j+1)+": "+p,["A","B","C","D","E"],unit["matchAnswers"][j])
        for j,p in enumerate(unit["matchPeople"])]
    reading2=[{"stem":stem,"answers":[ans]} for stem,ans in unit["reading2Questions"]]
    prefix="g9-"+unit["model"]
    tasks=[
      dict(id=prefix+"-L1",skill="listening",group=1,marks=5,
        title="Listening 1 — Choose the picture",items=imageItems,
        transcript="\n\n".join("Text "+str(j+1)+". "+x["script"] for j,x in enumerate(imageItems)),
        audio="audio/"+prefix.lower()+"-unit-v2-listening-1-two-pass.mp3"),
      dict(id=prefix+"-L2",skill="listening",group=2,marks=5,
        title="Listening 2 — Interview",items=interviewItems,transcript=interview,
        audio="audio/"+prefix.lower()+"-listening-2.mp3"),
      dict(id=prefix+"-GV",skill="grammar_vocabulary",group=1,marks=10,
        title="Grammar and Vocabulary — ten gaps",passage=gvText,items=gvItems),
      dict(id=prefix+"-R1",skill="reading",group=1,marks=4,
        title="Reading 1 — Matching",passage="Match four learners to five activities. One extra.",
        people=unit["matchPeople"],options=unit["matchOptions"],items=reading1),
      dict(id=prefix+"-R2",skill="reading",group=2,marks=6,
        title="Reading 2 — Short answers",passage=practice["reading"]["passage"],
        items=reading2),
      dict(id=prefix+"-W1",skill="writing",group=1,marks=5,
        title="Writing 1 — Story",prompt=unit["writing1"],minWords=100),
      dict(id=prefix+"-W2",skill="writing",group=2,marks=5,
        title="Writing 2 — Email",prompt=unit["writing2"],minWords=100)]
    assert len(tasks)==7 and sum(t["marks"] for t in tasks)==40
    assert sum(len(t.get("items",[])) for t in tasks)==30
    assert len(unit["interview"])==14
    models.append(dict(model=unit["model"],grade=9,semester=1,unit=i,
        unitTitle=unit["title"],minutes=120,marks=40,tasks=tasks,
        teacherReviewPending=True,certifiedTextbookMatch=False,
        status="original_unit_aligned_teacher_review_paper"))
result=dict(grade=9,semester=1,series="Gold Experience Oman 9A Trial Edition 2026",
    models=models,notLegacyRecycled=True,approvedByTeacher=False)
(OUT/"models.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print("CREATED",len(models),"original Grade9 unit paper drafts",sum(len(m["tasks"]) for m in models),"tasks")
