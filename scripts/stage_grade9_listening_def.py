#!/usr/bin/env python3
"""Temporarily overlay independently authored Grade 9 listening D/E/F.

Do not commit the changed grade9/data.js until the 45 new images and 6 MP3s
have been teacher reviewed and published in the same release.
"""
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'grade9/data.js'
JSON_BANK=ROOT/'grade9/data.json'
FILES=[ROOT/f'review/grade9-model-{letter.lower()}-original-listening.json' for letter in ('D','E','F')]

def validate_and_load():
 import sys
 sys.path.insert(0,str(ROOT/'scripts'))
 from listening_voice_roles import parse_dialogue
 docs=[json.loads(p.read_text(encoding='utf-8')) for p in FILES]
 assert {d['model'] for d in docs}=={'D','E','F'}
 all_images=[]
 for d in docs:
  l1,l2=d['listening1'],d['listening2']
  assert len(l1['items'])==len(l2['items'])==5,d['model']
  assert l1['id']==f"g9-{d['model']}-L1"
  assert l2['id']==f"g9-{d['model']}-L2"
  for item in l1['items']:
   assert len(item['choices'])==len(item['images'])==3
   assert 0<=item['answer']<3
   assert len(item['script'].split())>=35
   all_images.extend(item['images'])
  for q in l2['items']:
   assert len(q['choices'])==3 and 0<=q['answer']<3 and q.get('evidence')
  turns=parse_dialogue(l2['transcript'],l2['speakerGenders'])
  assert len(turns)>=12,(d['model'],'too few speech turns')
  cast=set(l2['speakerGenders'])
  assert {name for _,_,name in turns}==cast
 assert len(all_images)==45 and len(set(all_images))==45,'Repeated image IDs'
 src=BANK.read_text(encoding='utf-8')
 assert src.startswith('const EXAM_DATA=')
 data=json.loads(src.removeprefix('const EXAM_DATA=').rstrip(';\n '))
 snapshot=json.loads(JSON_BANK.read_text(encoding='utf-8'))
 assert {m['model']:tuple(t['id'] for t in m['tasks'] if t.get('skill')=='listening') for m in snapshot['models']}=={m['model']:tuple(t['id'] for t in m['tasks'] if t.get('skill')=='listening') for m in data['models']},'JSON and JS source model IDs disagree'
 original={m['model']:m for m in data['models']}
 expected={'D':('A','B'),'E':('B','C'),'F':('C','A')}
 for key,(m1,m2) in expected.items():
  current=original[key]
  first=next(t for t in current['tasks'] if t.get('skill')=='listening' and t.get('group')==1)
  second=next(t for t in current['tasks'] if t.get('skill')=='listening' and t.get('group')==2)
  old1=next(t for t in original[m1]['tasks'] if t.get('skill')=='listening' and t.get('group')==1)
  old2=next(t for t in original[m2]['tasks'] if t.get('skill')=='listening' and t.get('group')==2)
  assert first['id']==old1['id'] and second['id']==old2['id'],('Model changed',key)
 print('STAGE validated 3 independent Grade 9 models, 15 new short texts, 3 new interviews, 45 unique image IDs')
 return data,docs

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--apply',action='store_true',help='ONLY in disposable CI checkout; never direct push')
 args=p.parse_args()
 data,docs=validate_and_load()
 if not args.apply:
  print('DRY RUN: no bank modified')
  return
 models={m['model']:m for m in data['models']}
 for d in docs:
  m=models[d['model']]
  for group,label in ((1,'listening1'),(2,'listening2')):
   draft=d[label]
   task=next(t for t in m['tasks'] if t.get('skill')=='listening' and t.get('group')==group)
   task['id']=draft['id']
   task['items']=draft['items']
   task['transcript']=draft['transcript']
   task['audio']=draft['audio']
   if group==2: task['speakerGenders']=draft['speakerGenders']
   task['sourceStatus']='unique-review-preview-only'
 data_string='const EXAM_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n'
 BANK.write_text(data_string,encoding='utf-8')
 JSON_BANK.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('STAGE overlaid both Grade 9 JS and JSON sources in throwaway checkout')
if __name__=='__main__':main()
