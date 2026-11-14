#!/usr/bin/env python3
"""Strict structural and asset audit for 4 Grade 12 Elective fixed unit papers.
Tests task counts, text lengths, objective keys, chart evidence and audio script hashes.
Passing structural QA is NOT textbook-page certification or teacher approval.
"""
import hashlib
import json
import pathlib
from collections import Counter
ROOT=pathlib.Path(__file__).resolve().parents[1]
BANK=ROOT/"grade12/elective/units"
NAMES=["The arts","Doing the right thing","Living in a Changing World","Higher Education"]
TASKS=("listening1","listening2","reading1","reading2","writing")
VALID=("mc","tf","short","gap","note","match")
sections_expected={"listening1":(10,10),"listening2":(10,10),"reading1":(12,12),"reading2":(13,13)}
issue_count=0
texts={}
all_papers=[]
def require(test, message):
    global issue_count
    if not test:raise AssertionError(message)
def load(p):
    require(p.is_file(),"Missing "+str(p.relative_to(ROOT)))
    return json.loads(p.read_text(encoding="utf-8"))
for num,unit_name in enumerate(NAMES,1):
    parts={key:load(BANK/f"unit{num}-{key}-original-draft.json") for key in TASKS}
    for kind,data in parts.items():
        require(data["unit"]=={"number":num,"title":unit_name},f"Wrong unit source {num} {kind}")
        require(data.get("certifiedTextbookMatch") is False, f"Unapproved textbook claim in {num} {kind}")
        require(data.get("readyForStudentExam") is False,f"Unapproved final exam claim {num} {kind}")
    marks=[10,10,12,13,15,10]
    require(sum(marks)==70,"Required paper marks not 70")
    source=[]
    for kind,limit,needed in (("listening1",(400,450),10),("listening2",(450,500),10),("reading1",(450,500),12),("reading2",(450,500),13)):
        d=parts[kind]
        full=d.get("script") if kind.startswith("listening") else d.get("passage")
        words=len(full.split())
        require(d.get("wordCount")==words and limit[0]<=words<=limit[1],f"Wrong {num} {kind} length {words}")
        require(len(d["questions"])==needed,f"Wrong {num} {kind} item count")
        require(d["marks"]==sections_expected[kind][0] if kind in ("listening1","listening2","reading1","reading2") else True,f"Wrong {num} {kind} marks")
        require(all(q["type"] in VALID for q in d["questions"]),f"Unknown question type {num} {kind}")
        require(all(q.get("stem","").strip() for q in d["questions"]),f"Missing stem {num} {kind}")
        for q in d["questions"]:
            if q.get("options") is not None:
                require(isinstance(q["answer"],int) and 0<=q["answer"]<len(q["options"]),f"Bad objective answer {num} {kind}")
                require(len(q["options"])==(2 if q["type"]=="tf" else 8 if q["type"]=="match" else 3),f"Option count mismatch {num} {kind}")
            else:
                require(isinstance(q.get("answer"),str) and q["answer"].strip(),f"Missing short answer {num} {kind}")
                require(len(q["answer"].split())<=q["maxWords"],f"Answer exceeds word limit {num} {kind} {q['stem']}")
        h=hashlib.sha256(full.encode()).hexdigest()
        require(h not in texts,f"Duplicate source text across units: {texts.get(h)} and {num} {kind}")
        texts[h]=(num,kind)
        source.append({"section":kind,"words":words,"questions":needed,"sha256":h})
    l1,l2,r1,r2=parts["listening1"],parts["listening2"],parts["reading1"],parts["reading2"]
    require(len(l1["script"].splitlines())==l1["speakerTurns"] and 25<=l1["speakerTurns"]<=30,f"Dialogue turns {num}")
    require([q["type"] for q in l1["questions"]]==["mc"]*6+["tf"]*4,f"L1 item shapes {num}")
    require([q["type"] for q in l2["questions"]]==["note"]*5+["short"]*5,f"L2 item shapes {num}")
    require([q["type"] for q in r1["questions"]]==["short"]*7+["gap"]*5,f"R1 item shapes {num}")
    require([q["type"] for q in r2["questions"]]==["mc"]*8+["match"]*5,f"R2 item shapes {num}")
    require(sum(q.get("kind")=="meaning" for q in r2["questions"])==3,f"R2 meaning count {num}")
    require(len(r2["headings"])==8 and len(set(r2["headings"]))==8,f"R2 heading distractors {num}")
    require(len(r2["passage"].split("Paragraph "))==6,f"Need five labelled paragraphs in unit {num}")
    w=parts["writing"]
    require(w["writing1"]["marks"]==15 and w["writing2"]["marks"]==10,f"Writing allocation {num}")
    require(w["writing1"]["minWords"]>=150 and w["writing2"]["minWords"]>=150,f"Writing minimum {num}")
    require(w["writing1"]["prompt"] and w["writing2"]["prompt"],f"Writing prompt missing {num}")
    chart=w["writing2"]["chart"]
    require(len(chart["categories"])>=3 and len(chart["series"])==2,f"Chart structure invalid {num}")
    require(all(len(s["values"])==len(chart["categories"]) for s in chart["series"]),f"Chart data mismatch {num}")
    all_papers.append({"unit":num,"title":unit_name,"marks":70,"sections":6,"objectiveAndShortItems":45,"writingTasks":2,"sources":source})

manifest_path=BANK/"audio/manifest.json"
audit_audio={}
if manifest_path.exists():
    manifest=load(manifest_path)
    for num in range(1,5):
        for n in (1,2):
            src=f"unit{num}-listening{n}-original-draft.json"
            entry=manifest.get(src)
            if not entry:
                audit_audio[src]={"available":False}
                continue
            track=BANK/"audio"/entry["mp3"]
            source=load(BANK/src)
            sha=hashlib.sha256(source["script"].encode()).hexdigest()
            require(sha==entry["scriptSha256"],"Stale audio script source: "+src)
            require(track.is_file() and track.stat().st_size>25000,"MP3 missing or too small: "+src)
            require(entry.get("scriptReadTwice") is True,"Audio repeated-play instructions invalid: "+src)
            audit_audio[src]={"available":True,"sizeBytes":track.stat().st_size,"seconds":entry["durationSeconds"],"sha256":sha}
else:
    audit_audio={"status":"MP3 manifest not yet generated: teacher script still needed"}
report={"scope":"Grade 12 Elective, semester 1, four fixed 70-mark unit papers","teacherApproved":False,"officiallyCertified":False,"fixedUnitPapers":all_papers,"audioAudit":audit_audio,"note":"Syntactic QA, counts and linked audio hashes do not prove textbook page-level alignment or listening naturalness."}
print(json.dumps(report,ensure_ascii=False,indent=2))
