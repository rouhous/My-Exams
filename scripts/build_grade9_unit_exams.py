#!/usr/bin/env python3
"""Build original 7-task Grade 9 unit-specific exams from checked source data."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"grade9/unit-exams"
source=json.loads((OUT/"source-content.json").read_text())
skills=json.loads((ROOT/"grade9/unit-remediation/units.json").read_text())
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
    gvQs=practice["grammar"][:6]+practice["vocabulary"][:4]
    gvItems=[choice("Gap "+str(j+1),q["options"],q["answer"]) for j,q in enumerate(gvQs)]
    gvText="\n".join(str(j+1)+". "+q["stem"] for j,q in enumerate(gvQs))
    reading1=[choice("Person "+str(j+1)+": "+p,["A","B","C","D","E"],unit["matchAnswers"][j])
        for j,p in enumerate(unit["matchPeople"])]
    reading2=[{"stem":stem,"answers":[ans]} for stem,ans in unit["reading2Questions"]]
    prefix="g9-"+unit["model"]
    tasks=[
      dict(id=prefix+"-L1",skill="listening",group=1,marks=5,
        title="Listening 1 — Choose the picture",items=imageItems,
        transcript="\n\n".join("Text "+str(j+1)+". "+x["script"] for j,x in enumerate(imageItems)),
        audio="audio/"+prefix.lower()+"-listening-1.mp3"),
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
