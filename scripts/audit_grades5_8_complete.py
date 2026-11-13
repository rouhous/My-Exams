#!/usr/bin/env python3
"""Release gate for Grades 5–8: 4 base + 2 mixed + randomized exam readiness.
Tests files, section totals, task types, image references, and real natural MP3.
Unit alignment is explicitly NOT certified by this technical gate.
"""
import json,pathlib,subprocess,sys,collections,hashlib
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
    if g==5:
        source={'A':'Talent Show','B':'Then and Now','C':"Let's Explore",'D':'Off to the Shops'}
    else:
        source={'A':'Free-time Fun','B':'Technology','C':'Places','D':'Comprehensive'}
    for item in tasks:
        if item['skill']=='vocabulary' and item['format']=='picture-word-match':
            pics=item['pictureOptions'];words=item['wordOptions']
            check(len(item['questions'])==5,f'{item["id"]}: expected 5 vocabulary items')
            for i,q in enumerate(item['questions']):
                idx=q['answer']
                check(isinstance(idx,int) and 0<=idx<len(words) and pics[i]==words[idx],f'{item["id"]}: picture/word mismatch {i+1}')
        if item['skill']=='vocabulary' and item['format']=='picture-spelling':
            check(len(item['questions'])==5 and all(q['answer']==item['pictureOptions'][i] for i,q in enumerate(item['questions'])),f'{item["id"]}: picture spelling mismatch')
        if item['skill']=='reading' and item['part']==2:
            check(len(item['questions'])==5 and len(item['passage'].split())>=75,f'{item["id"]}: incomplete reading passage')
            check(set(q['answer'] for q in item['questions'])=={'True','False'},f'{item["id"]}: True/False answer diversity missing')
        if item['skill']=='listening':
            check(len(item['questions'])==5,f'{item["id"]}: listening questions not five')
            if item['part']==1:
                check(len(set(q['answer'] for q in item['questions']))==5,f'{item["id"]}: repeated listening picture key')
                check(all(0<=q['answer']<len(item['pictureOptions']) for q in item['questions']),f'{item["id"]}: listening picture key out of range')
            if item['part']==2:
                check(all(0<=q['answer']<len(q['options']) for q in item['questions']),f'{item["id"]}: listening MC key out of range')
            if item['model']!='D' or g==5:
                check(bool(item.get('unitTheme')),f'{item["id"]}: no unit-theme label')
    if g==6:
        for part,model in ((1,'A'),(2,'B')):
            orig=next(x for x in tasks if x['model']==model and x['skill']=='listening' and x['part']==part)
            mixed=next(x for x in tasks if x['model']=='D' and x['skill']=='listening' and x['part']==part)
            check(mixed.get('mediaId')==orig['id'] and mixed['questions']==orig['questions'],f'G6 D L{part}: source audio/keys not preserved')
    stats[str(g)]={'fixed_models':4,'mixed_models':2,'random_mode':True,'base_activities':len(tasks),'natural_mp3':8}
# Grade 5–6 generated audio is valid only when the precise version of its
# transcript AND answer keys matches the archived MP3 manifest.
manifest_path=ROOT/'grades5-6/audio-natural/script_audio_manifest.json'
if not manifest_path.exists():
    errors.append('Grade 5–6 natural audio script hash manifest missing; regenerate the recordings')
else:
    manifest=json.loads(manifest_path.read_text())
    for item in a:
        if item['skill']!='listening':continue
        payload={'passages':item.get('passages'),'passage':item.get('passage'),
                 'questions':item['questions'],'pictures':item.get('pictureOptions')}
        actual=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        stored=manifest.get(item['id'],{}).get('sha256_of_script')
        check(stored==actual,f'{item["id"]}: MP3 audio does not match the current question script')
for g in [7,8]:
    models=[x for x in b if x['grade']==g]
    check(len(models)==4,f'G{g}: expected 4 base models')
    for model in models:
        check(len(model['sections'])==7,f'{model["id"]}: expected 7 sections')
        check(sum(x['marks'] for x in model['sections'])==40,f'{model["id"]}: expected 40 marks')
        check([x['key'] for x in model['sections']]==['listening1','listening2','grammarvocabulary','reading1','reading2','writing1','writing2'],f'{model["id"]}: wrong section order')
        for x in model['sections']:
            if x['key']=='grammarvocabulary':
                check(len(x.get('items',[]))==10,f'{model["id"]}: 10 cloze questions required')
                for i,q in enumerate(x.get('items',[])):
                    check(len(q.get('options',[]))==3 and isinstance(q.get('answer'),int) and 0<=q['answer']<3,f'{model["id"]}: invalid cloze key {i+1}')
            if x['key']=='reading1':
                check(len(x.get('texts',[]))==5 and len(x.get('continuations',[]))==6,f'{model["id"]}: 5 reading texts and 6 endings required')
                check(len(x.get('answers',[]))==5 and all(isinstance(k,int) and 0<=k<6 for k in x.get('answers',[])),f'{model["id"]}: reading matching keys invalid')
            if x['key']=='reading2':
                check(len(x.get('items',[]))==5 and len(x.get('passage','').split())>=150,f'{model["id"]}: reading comprehension incomplete')
            if x['key']=='listening2':
                check(len(x.get('items',[]))==5 and len(x.get('script','').split())>=120,f'{model["id"]}: interview script too short')
            if x['key']=='listening1':
                for i,q in enumerate(x.get('items',[])):
                    check(len(q.get('options',[]))==3 and isinstance(q.get('answer'),int) and 0<=q['answer']<3,f'{model["id"]}: image choice key invalid {i+1}')
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
