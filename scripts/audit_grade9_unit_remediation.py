#!/usr/bin/env python3
"""Strict standalone content-integrity audit: 2026 Gold Experience Oman Grade 9 unit drills.
This is NOT verification of the full ministerial exam nor of audio/visual approval.
"""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
p=root/"grade9/unit-remediation/units.json"
d=json.loads(p.read_text(encoding="utf-8"))
names=["Identity","Connections","The future is now"]
assert d["grade"]==9 and d["semester"]==1
assert "NOT_full" in d["status"],"Supplemental bank must never masquerade as complete exam"
assert len(d["units"])==3
texts=set()
for index,u in enumerate(d["units"],1):
    assert u["number"]==index and u["title"]==names[index-1]
    assert len(u["grammar"])==7 and len(u["vocabulary"])==5
    assert len(u["reading"]["questions"])==4 and len(u["writing"])==2
    assert len(u["reading"]["passage"].split())>=145
    assert u["reading"]["passage"] not in texts
    texts.add(u["reading"]["passage"])
    for group in ("grammar","vocabulary"):
        for q in u[group]:
            assert len(q["options"])==3,(index,group,q)
            assert isinstance(q["answer"],int) and 0<=q["answer"]<3,(index,group,q)
            assert q["options"][q["answer"]].strip()
            if group=="grammar":assert q["explanation"].strip()
    for q in u["reading"]["questions"]:
        assert len(q["options"])==3 and 0<=q["answer"]<3
    for w in u["writing"]:
        assert w["minWords"]>=80 and len(w["prompt"])>=60
html=(root/"grade9/unit-remediation/index.html").read_text(encoding="utf-8")
assert "Writing · teacher review required" in html
assert "For a full 120-minute exam" in html
assert "units.json" in html
assert "no timer" in html.lower()
assert "grade9/unit-remediation/index.html" in (root/"sw.js").read_text(encoding="utf-8")
assert "./unit-remediation/index.html" in (root/"grade9/index.html").read_text(encoding="utf-8")
print("PASS: 3 units, 48 objective items, 6 ungraded writing prompts; no unrelated full-exam or listening-audio claim")
