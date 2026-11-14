#!/usr/bin/env python3
"""Audit curriculum-targeted fixes without falsely releasing full Ministry unit exams.
Scope is exclusively Grades 9, 11 and 12; Grade 10 and Grades 5-8 are intentionally untouched.
"""
import hashlib,json,pathlib,sys
from collections import Counter
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def words(s):return len(s.strip().split())
def check(v,msg):
    if not v:raise AssertionError(msg)
results={"scope":{"grades":[9,11,12],"semester":1},"grade9":{},"grade11":{},"grade12":{},"teacherApproved":False}
b=read("grade9/unit-remediation/units.json")
check([u["title"] for u in b["units"]]==["Identity","Connections","The future is now"],"Grade9 unit titles wrong")
counts=[(len(u["grammar"])+len(u["vocabulary"])+len(u["reading"]["questions"]),len(u["writing"])) for u in b["units"]]
check(counts==[(16,2)]*3,"Grade9 unit practice question counts wrong")
results["grade9"]={"newUntimedUnitPractice":3,"newObjectiveItems":sum(x for x,y in counts),"newWritingPrompts":sum(y for x,y in counts),"newFullExams":0,"existingFixedExamModels":7,"listeningAudioPolicy":"existing Grade9 A-G original source-matched recordings kept; no new listening sections in remediation"}
upper=read("higher_grades_corrected.json")
for track in ("11-elective","12-core"):
    models=[m for m in upper[track] if m["id"] in "ABCD"]
    check(len(models)==4,"Original upper bank unexpectedly altered")
    check(all("coastal research" not in p.get("prompt","").lower() for m in models for p in m["parts"] if p["key"].startswith("wrt")),"Old unrelated writing prompts remain")
results["grade11"]["electiveLegacyWritingCorrected"]=8
results["grade12"]["coreLegacyWritingCorrected"]=8
m=next(m for m in read("grade11/core/data.json")["models"] if m["id"]=="D")
check(len(m["reading"]["questions"])==20 and "prototype" in m["reading"]["passage"].lower(),"Grade 11 core innovation reading not corrected")
results["grade11"]["coreUnit4PilotReadingCorrected"]=True
tracks=[
("11-elective","grade11/elective/units",[(1,(400,450),10,10),(2,(400,450),10,10)],"grade11"),
("12-core","grade12/core/units",[(1,(350,450),7,7),(2,(350,450),8,8)],"grade12")
]
for track,folder,sections,grade in tracks:
    manpath=ROOT/folder/"audio/manifest.json"
    manifest=read(str(pathlib.PurePosixPath(folder)/"audio/manifest.json")) if manpath.is_file() else {}
    found=0
    for n,limits,marks,nq in sections:
        filename=f"unit1-listening{n}-original-draft.json";src=read(f"{folder}/{filename}")
        wc=words(src["script"])
        check(limits[0]<=wc<=limits[1] and wc==src["wordCount"],f"{track} Listening {n} length {wc}")
        check(src["marks"]==marks and len(src["questions"])==nq,f"{track} Listening {n} items")
        types=[q["type"] for q in src["questions"]]
        expected=(["mc"]*6+["tf"]*4 if track=="11-elective" and n==1 else
                  ["short"]*6+["gap"]*4 if track=="11-elective" else
                  ["mc"]*7 if n==1 else ["short"]*4+["mc"]*4)
        check(types==expected,f"{track} Listening {n} task shape {types}")
        for q in src["questions"]:
            if q.get("options") is not None:
                check(isinstance(q["answer"],int) and 0<=q["answer"]<len(q["options"]),f"{track} objective key")
                check(len(q["options"]) in (2,3),f"{track} choice count")
            else:check(isinstance(q.get("answer"),str) and q["answer"],f"{track} short answer")
        if n==1:check(25<=src["speakerTurns"]<=30,f"{track} dialogue turns")
        if track=="12-core" and n==2:check("Part One" in src["script"] and "Part Two" in src["script"],"12 core monologue parts")
        entry=manifest.get(filename)
        if entry:
            dest=ROOT/folder/"audio"/entry["mp3"]
            check(entry["scriptSha256"]==hashlib.sha256(src["script"].encode()).hexdigest(),f"{track} stale MP3 manifest")
            check(dest.is_file() and dest.stat().st_size>25000,f"{track} missing MP3")
            check(entry["scriptReadTwice"] is True,f"{track} audio play count")
            found+=1
    results[grade][track.replace("-","_")+"_newUnit1Listening"]={"sectionsWithDrafts":2,"audioSourceVerified":found,"audioRequired":2,"completeFullUnitPapers":0,"teacherReviewRequired":True}
print(json.dumps(results,ensure_ascii=False,indent=2))
