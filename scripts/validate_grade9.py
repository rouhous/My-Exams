#!/usr/bin/env python3
"""My Exams Grade 9 structural and media preflight. No Ministry certification implied."""
import json, pathlib, sys, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'grade9/data.json').read_text(encoding='utf-8'))
MODELS=DATA['models']
ERRORS=[]
REPORT=[]
EXPECTED=[('listening',1,5,5),('listening',2,5,5),('grammar_vocabulary',1,10,10),
          ('reading',1,4,4),('reading',2,6,6),('writing',1,5,0),('writing',2,5,0)]
for m in MODELS:
    tags=[]
    if len(m['tasks'])!=7:ERRORS.append(f"{m['model']}: expected 7 sections")
    if int(m.get('minutes',120))!=120 or sum(t['marks'] for t in m['tasks'])!=40:
        ERRORS.append(f"{m['model']}: time/marks mismatch")
    for i,(skill,group,mark,items) in enumerate(EXPECTED):
        if i>=len(m['tasks']):break
        t=m['tasks'][i]
        if t['skill']!=skill or int(t.get('group',1))!=group or t['marks']!=mark:
            ERRORS.append(f"{m['model']}:{i} incorrect section/mark")
        if len(t.get('items',[]))!=items:
            ERRORS.append(f"{m['model']}:{i} incorrect item count")
        if skill=='listening':
            if not (ROOT/'grade9'/t.get('audio','--missing--')).is_file():
                ERRORS.append(f"{m['model']}:{i} local backup MP3 missing")
            if group==1:
                for q in t['items']:
                    if len(q.get('images',[]))!=3:ERRORS.append(f"{m['model']}: listening picture count")
                    for p in q.get('images',[]):
                        if not (ROOT/'grade9'/p).is_file():ERRORS.append(f"{m['model']}: missing image {p}")
        if skill=='grammar_vocabulary':
            n=len(t['passage'].split())
            if not (80<=n<=90):ERRORS.append(f"{m['model']}: cloze words={n}")
            if any(len(q.get('choices',[]))!=4 for q in t['items']):ERRORS.append(f"{m['model']}: cloze choices")
        if skill=='reading' and group==1:
            if len(t.get('people',[]))!=4 or len(t.get('options',[]))!=5:ERRORS.append(f"{m['model']}: R1 matching count")
            if any(not 0<=q.get('answer',-1)<5 for q in t['items']):ERRORS.append(f"{m['model']}: R1 answer index")
        if skill=='reading' and group==2:
            n=len(t['passage'].split())
            if not 250<=n<=300:ERRORS.append(f"{m['model']}: R2 words={n}")
        if skill=='writing' and t.get('minWords',0)<100:
            ERRORS.append(f"{m['model']}: writing minimum less than 100")
        tags.append(t['id'])
    REPORT.append({'model':m['model'],'tasks':tags,'marks':sum(t['marks'] for t in m['tasks'])})
SRC=json.loads((ROOT/'NATURAL_AUDIO_SOURCES.json').read_text(encoding='utf-8'))
for model,minimum in [('a',21),('b',20)]:
    natural=[p for p in SRC if f'/g9/{model}/' in p['file']]
    if len(natural)!=minimum:ERRORS.append(f"{model} natural voice manifest count {len(natural)} != {minimum}")
    for item in natural:
        path=ROOT/item['file']
        if not path.is_file() or path.stat().st_size<1024:
            ERRORS.append(f"Natural MP3 missing/invalid: {item['file']}")
if len(MODELS)!=7:ERRORS.append(f"Unexpected Grade 9 fixed model count {len(MODELS)}")
OUT={'grade':9,'fixed_models':len(MODELS),'random_mode_in_ui':"buildRandomModel" in (ROOT/'grade9/index.html').read_text(), 'natural_mp3_expected':41,'checks_passed':not ERRORS,'issues':ERRORS,'models':REPORT,'note':'Content/unit-level teacher review and real-device offline acceptance are separate checks.'}
(ROOT/'grade9/teacher/QA_RUN_REPORT.json').write_text(json.dumps(OUT,indent=2)+'\n',encoding='utf-8')
print(json.dumps(OUT,ensure_ascii=False,indent=2))
if ERRORS:sys.exit(1)
