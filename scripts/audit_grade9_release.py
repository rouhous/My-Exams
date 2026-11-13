#!/usr/bin/env python3
"""Audit every Grade 9 model and its shared listening media."""
import json, pathlib, collections, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=ROOT/'grade9'
models=json.loads((base/'data.json').read_text())['models']
errors=[];warnings=[]
for m in models:
    name=m['model']
    tasks=m['tasks']
    if len(tasks)!=7:errors.append(f'{name}: expected 7 tasks, got {len(tasks)}')
    if sum(t.get('marks',0) for t in tasks)!=40:errors.append(f'{name}: marks != 40')
    if m.get('minutes')!=120:errors.append(f'{name}: time != 120')
    for t in tasks:
        if t.get('skill')=='listening':
            if not (base/t['audio']).exists():errors.append(f'{name}/{t["id"]}: backup MP3 missing')
            if t['group']==1:
                for i,item in enumerate(t['items']):
                    if len(item.get('images',[]))!=3:errors.append(f'{name}/{t["id"]}/{i}: expected 3 pictures')
                    for img in item.get('images',[]):
                        if not (base/img).is_file():errors.append(f'{name}/{t["id"]}/{i}: missing {img}')
                    if not item.get('script'):errors.append(f'{name}/{t["id"]}/{i}: missing listening script')
            if t['group']==2 and not t.get('transcript'):errors.append(f'{name}/{t["id"]}: interview transcript missing')
        for i,item in enumerate(t.get('items',[])):
            if 'choices' in item and isinstance(item.get('answer'),int):
                if not 0<=item['answer']<len(item['choices']):errors.append(f'{name}/{t["id"]}/{i}: invalid answer')
    if name in ('D','E','F'):warnings.append(f'{name}: mixed model intentionally reuses items from unit banks A/B/C')
    if name in ('A','B','C','G'):warnings.append(f'{name}: exact curriculum unit alignment not independently certified')
report={
 'grade':9,'models':[m['model'] for m in models],
 'models_count':len(models),'task_count':sum(len(m['tasks']) for m in models),
 'total_marks_per_model':40,'minutes_per_model':120,
 'image_reference_errors':[e for e in errors if 'picture' in e or 'missing images/' in e],
 'errors':errors,'warnings':warnings,
 'natural_audio_status':'A uses 21 verified natural segments; B/C/G neural MP3 generation requires verified action success',
 'final_curriculum_approval':False
}
out=base/'teacher'/'GRADE9_RELEASE_QA.json';out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:sys.exit(1)
