#!/usr/bin/env python3
"""Strict source and Ministry-form QA of the five newly built G11/G12 Core unit papers.
Teacher approval remains false; missing TTS is explicitly reported, never claimed complete.
"""
import hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
units=[
(11,1,'a','Communication'),(11,3,'c','Travellers and Tourists'),(11,4,'d','Innovation'),
(12,3,'c','Tourism and Hospitality'),(12,4,'d','Travel and Transport')]
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def wordcount(s):return len(s.split())
def ck(condition,message):
    if not condition:raise AssertionError(message)
report={"papers":[],"requiredMedia":10,"verifiedMedia":0,"pendingMedia":[],"teacherApproved":False}
for grade,n,letter,title in units:
    base=root/f"grade{grade}/core/units"
    paper=read(base/f"unit{n}-paper-{letter}.json")
    ck(paper['grade']==grade and paper['track']=='core',f"{grade} U{n} track")
    ck(paper['unit']=={"number":n,"title":title},f"{grade} U{n} title")
    ck(paper['marks']==(60 if grade==11 else 70),f"{grade} U{n} marks")
    ck(paper['durationMinutes']==(150 if grade==11 else 180),f"{grade} U{n} minutes")
    ck(paper['certifiedTextbookMatch'] is False and paper['readyForStudentExam'] is False,f"{grade} U{n} release")
    s=paper['sections']
    marks={"grm":5,"vcb":5,"rdg1":5 if grade==11 else 7,"rdg2":7 if grade==11 else 8,"rdg3":8 if grade==11 else 10,"wrt1":5 if grade==11 else 10,"wrt2":10}
    ck(set(s)==set(marks),f"{grade} U{n} missing section")
    for k,v in marks.items():ck(s[k]['marks']==v,f"{grade} U{n} {k} marks")
    bounds={"grm":(50,60) if grade==11 else (60,70),"vcb":(70,80) if grade==11 else (80,90),"rdg2":(300,350) if grade==11 else (350,400),"rdg3":(350,400) if grade==11 else (400,450)}
    for key,(lo,hi) in bounds.items():
        ck(s[key]['wordCount']==wordcount(s[key]['passage']),f"{grade} U{n} {key} declared words")
        ck(lo<=s[key]['wordCount']<=hi,f"{grade} U{n} {key} range")
    shortnum=5 if grade==11 else 7
    ck(len(s['rdg1']['texts'])==shortnum and len(s['rdg1']['questions'])==shortnum,f"{grade} U{n} short texts")
    for t,q in zip(s['rdg1']['texts'],s['rdg1']['questions']):
        ck(35<=wordcount(t['passage'])<=45,f"{grade} U{n} short text words")
        ck(t['statement']==q['stem'] and t['answer']==q['answer'],f"{grade} U{n} short text key")
    required={"grm":5,"vcb":5,"rdg1":shortnum,"rdg2":7 if grade==11 else 8,"rdg3":8 if grade==11 else 10}
    for k,count in required.items():
        qs=s[k]['questions'];ck(len(qs)==count,f"{grade} U{n} {k} questions")
        for q in qs:
            if 'options' in q:ck(0<=q['answer']<len(q['options']),f"{grade} U{n} {k} key")
            else:ck(isinstance(q.get('answer'),str) and bool(q['answer']),f"{grade} U{n} {k} short")
    ck(all(q['type']=='mc' and len(q['options'])==2 for q in s['grm']['questions']),f"{grade} U{n} grammar")
    ck(all(q['type']=='mc' and len(q['options'])==3 for q in s['vcb']['questions']),f"{grade} U{n} vocabulary")
    ck([q['type'] for q in s['rdg2']['questions']]==['mc']*(7 if grade==11 else 8),f"{grade} U{n} Reading2")
    ck([q['type'] for q in s['rdg3']['questions']]==['short']*(4 if grade==11 else 6)+['mc']*4,f"{grade} U{n} Reading3")
    ck(s['wrt1']['minWords']>=(85 if grade==11 else 100) and s['wrt2']['minWords']>=100,f"{grade} U{n} writing length")
    ck(sum(v['marks'] for v in s.values())+15==paper['marks'],f"{grade} U{n} sum")
    view=(base/f"paper-{letter}-preview.html").read_text(encoding='utf-8')
    ck(f"unit{n}-paper-{letter}.json" in view,f"{grade} U{n} preview wrong source")
    ck(f"unit{n}-listening1-original-draft.json" in view,f"{grade} U{n} preview missing Listening1")
    ck(f"unit{n}-listening2-original-draft.json" in view,f"{grade} U{n} preview missing Listening2")
    manifestpath=base/'audio/manifest.json'
    manifest=read(manifestpath) if manifestpath.exists() else {}
    verified=0
    for listening,lo,hi,qty,types in [(1,300 if grade==11 else 350,350 if grade==11 else 450,7,['mc']*7),(2,350,400 if grade==11 else 450,8,['short']*4+['mc']*4)]:
        filename=f"unit{n}-listening{listening}-original-draft.json"
        source=read(base/filename)
        ck(source['grade']==grade and source['unit']==paper['unit'],f"{grade} U{n} audio unit")
        ck(source['wordCount']==wordcount(source['script']),f"{grade} U{n} audio word count")
        ck(lo<=source['wordCount']<=hi,f"{grade} U{n} audio range")
        ck(len(source['questions'])==qty and [q['type'] for q in source['questions']]==types,f"{grade} U{n} audio questions")
        if listening==1:ck(25<=source['speakerTurns']<=30,f"{grade} U{n} audio dialogue turns")
        if listening==2:ck('Part One' in source['script'] and 'Part Two' in source['script'],f"{grade} U{n} audio parts")
        row=manifest.get(filename)
        if row:
            ck(row['scriptSha256']==hashlib.sha256(source['script'].encode()).hexdigest(),f"{grade} U{n} MP3 hash outdated")
            ck(row['scriptReadTwice'] is True,f"{grade} U{n} MP3 not repeated")
            path=base/'audio'/row['mp3']
            ck(path.exists() and path.stat().st_size>25000,f"{grade} U{n} MP3 missing")
            verified+=1
        else:report['pendingMedia'].append(f"grade{grade}/core/units/{filename}")
    report['verifiedMedia']+=verified
    report['papers'].append({"grade":grade,"unit":n,"title":title,"marks":paper['marks'],"sections":9,"verifiedMP3":verified,"requiredMP3":2,"teacherApproved":False})
print(json.dumps(report,ensure_ascii=False,indent=2))
(R:=root/'TARGETED_CORE_COMPLETENESS_2026-11-16.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
