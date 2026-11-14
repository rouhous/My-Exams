#!/usr/bin/env python3
"""Grade 11 elective The Mind original six-section 60-mark unit paper: SAH/MP3-integrity checks."""
import json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=ROOT/"grade11/elective/units"
def read(p):return json.loads((base/p).read_text(encoding="utf-8"))
def words(s):return len(s.strip().split())
parts={k:read(f"unit2-{k}-original-draft.json") for k in ("listening1","listening2","reading1","reading2","writing")}
for kind in ("listening1","listening2","reading1","reading2"):
    d=parts[kind]
    assert d["grade"]==11 and d["track"]=="elective" and d["unit"]=={"number":2,"title":"The Mind"},kind
    assert d["certifiedTextbookMatch"] is False and d["readyForStudentExam"] is False
    assert 400<=d["wordCount"]<=450 and d["wordCount"]==words(d.get("script") or d["passage"]),kind
    assert d["marks"]==10 and len(d["questions"])==10,kind
a,b,c,d=(parts[k] for k in ("listening1","listening2","reading1","reading2"))
assert 25<=a["speakerTurns"]<=30
assert [q["type"] for q in a["questions"]]==["mc"]*6+["tf"]*4
assert [q["type"] for q in b["questions"]]==["short"]*6+["gap"]*4
assert [q["type"] for q in c["questions"]]==["short"]*6+["tf"]*4
assert [q["type"] for q in d["questions"]]==["mc"]*6+["match"]*4
assert sum(q.get("kind")=="meaning" for q in d["questions"])==2
assert len(d["headings"])==7 and len(set(d["headings"]))==7 and d["paragraphs"]>=6
for kind in ("listening1","listening2","reading1","reading2"):
    for q in parts[kind]["questions"]:
        if q.get("options") is not None:
            assert isinstance(q["answer"],int) and 0<=q["answer"]<len(q["options"]),kind
            assert len(q["options"])==(2 if q["type"]=="tf" else 7 if q["type"]=="match" else 3),kind
        else: assert isinstance(q.get("answer"),str) and q["answer"].strip(),kind
w=parts["writing"]
assert w["writing1"]["marks"]==10 and w["writing2"]["marks"]==10
assert w["writing1"]["minWords"]>=100 and w["writing2"]["minWords"]>=100
chart=w["writing1"]["chart"]
assert len(chart["categories"])==4 and len(chart["series"])==1 and len(chart["series"][0]["values"])==4
man=read("audio/manifest.json")
for n in (1,2):
    source=parts[f"listening{n}"];file=f"unit2-listening{n}-original-draft.json"
    entry=man[file]
    assert entry["scriptSha256"]==hashlib.sha256(source["script"].encode()).hexdigest(),file
    assert entry["scriptReadTwice"] is True
    assert (base/"audio"/entry["mp3"]).stat().st_size>25000
assert all(p["unit"]["title"]=="The Mind" for p in parts.values())
print(json.dumps({"grade":11,"track":"elective","unit":"The Mind","sections":6,"marks":60,"minutes":150,"sourcesWordCounts":{k:parts[k]["wordCount"] for k in ("listening1","listening2","reading1","reading2")},"verifiedMP3":2,"objective":24,"manualShort":16,"writing":2,"certified":False},indent=2))
