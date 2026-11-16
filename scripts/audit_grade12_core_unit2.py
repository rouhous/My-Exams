#!/usr/bin/env python3
"""SAH-structured original Grade 12 Core Starting University Paper B integrity checks.
A successful check does NOT imply teacher-approved textbook page alignment or voice quality.
"""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=ROOT/"grade12/core/units"
def read(name):return json.loads((base/name).read_text(encoding="utf-8"))
def words(s):return len(s.strip().split())
paper=read("unit2-paper-a.json")
assert paper["grade"]==12 and paper["track"]=="core" and paper["unit"]=={"number":2,"title":"Starting University"}
assert paper["durationMinutes"]==180 and paper["marks"]==70
assert paper["certifiedTextbookMatch"] is False and paper["readyForStudentExam"] is False
expected={"grm":(5,5),"vcb":(5,5),"rdg1":(7,7),"rdg2":(8,8),"rdg3":(10,10),"wrt1":(10,0),"wrt2":(10,0)}
count=15
for k,(marks,qcount) in expected.items():
    s=paper["sections"][k]
    assert s["marks"]==marks,(k,"marks")
    assert len(s.get("questions",[]))==qcount,(k,"question count")
    if "passage" in s:assert s["wordCount"]==words(s["passage"])
    if k.startswith("wrt"):assert s["minWords"]>=100 and len(s["prompt"])>=100
    if "questions" in s:
        for q in s["questions"]:
            if "options" in q:
                assert isinstance(q["answer"],int) and 0<=q["answer"]<len(q["options"]),k
            else:assert isinstance(q.get("answer"),str) and q["answer"],k
for k,limit in [("grm",(60,70)),("vcb",(80,90)),("rdg2",(350,400)),("rdg3",(400,450))]:
    w=paper["sections"][k]["wordCount"]
    assert limit[0]<=w<=limit[1],(k,w)
r1=paper["sections"]["rdg1"]
assert len(r1["texts"])==7 and all(35<=words(t["passage"])<=45 for t in r1["texts"])
assert [q["type"] for q in r1["questions"]]==["tf"]*7
assert [q["type"] for q in paper["sections"]["rdg2"]["questions"]]==["mc"]*8
assert [q["type"] for q in paper["sections"]["rdg3"]["questions"]]==["short"]*6+["mc"]*4
assert [q["type"] for q in paper["sections"]["grm"]["questions"]]==["mc"]*5
assert all(len(q["options"])==2 for q in paper["sections"]["grm"]["questions"])
assert all(len(q["options"])==3 for q in paper["sections"]["vcb"]["questions"])
assert sum(x["marks"] for x in paper["sections"].values())+7+8==70
audio=read("audio/manifest.json")
for n,limit,qs,types in [(1,(350,450),7,["mc"]*7),(2,(350,450),8,["short"]*4+["mc"]*4)]:
    filename=f"unit2-listening{n}-original-draft.json"
    source=read(filename)
    assert limit[0]<=words(source["script"])<=limit[1]
    assert source["marks"]==qs and [q["type"] for q in source["questions"]]==types
    if n==1:assert 25<=source["speakerTurns"]<=30
    if n==2:assert "Part One" in source["script"] and "Part Two" in source["script"]
    entry=audio.get(filename)
    assert entry and entry["scriptReadTwice"] is True,(n,"No verified MP3")
    assert entry["scriptSha256"]==hashlib.sha256(source["script"].encode()).hexdigest(),(n,"stale MP3")
    p=base/"audio"/entry["mp3"]
    assert p.is_file() and p.stat().st_size>25000,(n,"missing audio")
assert sum(1 for k in ("lst1","lst2") for q in read(f"unit2-listening{1 if k=='lst1' else 2}-original-draft.json")["questions"] if q.get("options")) + sum(1 for s in paper["sections"].values() for q in s.get("questions",[]) if q.get("options"))==40
assert sum(1 for k in ("lst1","lst2") for q in read(f"unit2-listening{1 if k=='lst1' else 2}-original-draft.json")["questions"] if not q.get("options")) + sum(1 for s in paper["sections"].values() for q in s.get("questions",[]) if not q.get("options"))==10
print(json.dumps({"track":"Grade 12 Core","unit":"Starting University","sections":9,"marks":70,"minutes":180,"sourceVerifiedMP3":2,"objectiveQuestions":40,"teacherReviewedShortAnswers":10,"teacherReviewedWriting":2,"certified":False},indent=2))
