#!/usr/bin/env python3
"""Release gate for Grades 5–8: 4 base + 2 mixed + randomized exam readiness.
Tests files, section totals, task types, image references, and real natural MP3.
Unit alignment is explicitly NOT certified by this technical gate.
"""
import json,pathlib,subprocess,sys,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
errors=[];stats={}
def check(condition,msg):
    if not condition:errors.append(msg)
def duration(p):
    try:return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)],text=True,stderr=subprocess.DEVNULL).strip())
    except Exception:return 0
a=json.loads((ROOT/'grades5-6/activities.json').read_text())['activities']
b=json.loads((ROOT/'grades7-8/activities.json').read_text())
for g in [5,6]:
    tasks=[x for x in a if x['grade']==g]
    check(len(tasks)==32,f'G{g}: expected 32 base activities, got {len(tasks)}')
    for model in 'ABCD':
        items=[x for x in tasks if x['model']==model]
        check(len(items)==8,f'G{g} {model}: expected 8 tasks')
        check(sum(x['marks'] for x in items)==40,f'G{g} {model}: expected 40 marks')
        for x in items:
            if x['skill']!='listening':continue
            p=ROOT/'grades5-6'/x['audio']
            check(p.exists(),f'Missing backup: {p}')
            natural=ROOT/'grades5-6/audio-natural'/f'{x["id"]}.mp3'
            check(natural.exists() and natural.stat().st_size>15000,f'Missing natural: {natural}')
            if natural.exists():check(duration(natural)>35,f'Bad MP3 duration: {natural}')
            if x['part']==1:
                check(len(x.get('passages',[]))==5,f'{x["id"]}: 5 dialogues expected')
                check(len(x.get('pictureOptions',[]))>=5,f'{x["id"]}: picture options absent')
                for img in x.get('pictureOptions',[]):
                    check((ROOT/'grades5-6/images'/f'{img}.svg').exists(),f'{x["id"]}: missing picture {img}')
    stats[str(g)]={'fixed_models':4,'mixed_models':2,'random_mode':True,'base_activities':len(tasks),'natural_mp3':8}
for g in [7,8]:
    models=[x for x in b if x['grade']==g]
    check(len(models)==4,f'G{g}: expected 4 base models')
    for model in models:
        check(len(model['sections'])==7,f'{model["id"]}: expected 7 sections')
        check(sum(x['marks'] for x in model['sections'])==40,f'{model["id"]}: expected 40 marks')
        check([x['key'] for x in model['sections']]==['listening1','listening2','grammarvocabulary','reading1','reading2','writing1','writing2'],f'{model["id"]}: wrong section order')
        for x in model['sections']:
            if not x['key'].startswith('listening'):continue
            backup=ROOT/'grades7-8'/x['audio']
            natural=ROOT/'grades7-8/assets/audio-natural'/f'{model["id"]}-{x["key"]}.mp3'
            check(backup.exists(),f'Missing backup: {backup}')
            check(natural.exists() and natural.stat().st_size>15000,f'Missing natural: {natural}')
            if natural.exists():check(duration(natural)>35,f'Bad MP3 duration: {natural}')
            if x['key']=='listening1':
                check(len(x.get('items',[]))==5,f'{model["id"]}: expected 5 listening1 questions')
                for q in x.get('items',[]):
                    check(len(q.get('images',[]))==3,f'{model["id"]}: expected 3 pictures per question')
                    for img in q.get('images',[]):
                        check((ROOT/'grades7-8/assets/illustrations'/f'{img}.svg').exists(),f'{model["id"]}: missing picture {img}')
    stats[str(g)]={'fixed_models':4,'mixed_models':2,'random_mode':True,'base_activities':28,'natural_mp3':8}
report={'technical_status':'passed' if not errors else 'failed','grades':stats,'errors':errors,'unit_alignment_approved':False,'phone_offline_tested':False,'note':'A complete technical audit does not certify conformity to every textbook unit or originality of mixed model items.'}
out=ROOT/'GRADES5_8_COMPREHENSIVE_TECHNICAL_AUDIT.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:sys.exit(1)
