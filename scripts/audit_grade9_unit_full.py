#!/usr/bin/env python3
"""Grade9 Gold Experience Oman three NEW full papers: exact source audio, picture options, 40 marks and coherent clozes."""
import json,pathlib,hashlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
base=ROOT/'grade9/unit-exams'
bank=json.loads((base/'models.json').read_text())
manifest=json.loads((base/'audio/manifest.json').read_text())
assert len(bank['models'])==3 and len(manifest)==6
assert [m['unitTitle'].lower() for m in bank['models']]==['identity','connections','the future is now']
for m in bank['models']:
 assert m['grade']==9 and m['marks']==40 and m['minutes']==120 and len(m['tasks'])==7
 assert [x['marks'] for x in m['tasks']]==[5,5,10,4,6,5,5]
 for t in m['tasks'][:2]:
  src={'transcript':t.get('transcript'),'items':t.get('items'),'questions':t.get('questions')}
  digest=hashlib.sha256(json.dumps(src,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
  row=manifest[t['id']]
  assert row['sourceHash']==digest
  assert row['sourceTranscriptSha256']==hashlib.sha256(t['transcript'].encode()).hexdigest()
  f=base/'audio'/row['mp3'];assert f.stat().st_size>15000 and row['seconds']>40 and row['bytes']==f.stat().st_size
  assert f.open('rb').read(3)==b'ID3' or f.open('rb').read(1)==b'\xff'
  assert row['playedTwice'] is True
 # 2026-2027 official SAH Grade Nine Semester One, September 2026, printed p.53
 listening1,listening2,grammar,reading1,reading2,writing1,writing2=m['tasks']
 assert 200<=len(listening2['transcript'].split())<=250
 assert len(listening2['items'])==5 and all(len(q['choices'])==3 for q in listening2['items'])
 assert all(40<=len(q['script'].split())<=50 for q in listening1['items'])
 assert 70<=len(re.sub(r'\\(\\d+\\)\\s+_____', 'ANSWER', grammar['passage']).split())<=80, 'Cloze word count counts each gap as one completed word'
 assert all(len(q['choices'])==4 and 0<=q['answer']<4 for q in grammar['items'])
 assert len(grammar['items'])==grammar['passage'].count('_____')==10
 assert len(reading1['people'])==4 and len(reading1['options'])==5
 assert all(30<=len(p.split())<=35 for p in reading1['people'])
 assert all(50<=len(re.sub(r'^[A-E]:\\s*', '', o).split())<=55 for o in reading1['options']), 'Exclude option labels A–E from 50–55-word reading text count'
 assert 250<=len(reading2['passage'].split())<=300
 assert len(reading2['items'])==6 and all(len(q.get('answers',[]))>=1 for q in reading2['items'])
 assert writing1['minWords']>=100 and writing2['minWords']>=100
 assert len(m['tasks'][0]['items'])==5
 for q in m['tasks'][0]['items']:
  assert len(q['images'])==len(q['choices'])==3 and 0<=q['answer']<3
  for image in q['images']:assert (base/image).is_file(),image
 assert len(m['tasks'][1]['items'])==5
 assert len(m['tasks'][2]['items'])==10 and m['tasks'][2]['passage'].count('_____')==10
 assert len(m['tasks'][3]['items'])==4 and len(m['tasks'][4]['items'])==6
 assert sum(len(x.get('items',[])) for x in m['tasks'])==30
print('PASS Grade 9 SAH September 2026: three 40-mark original unit papers, 6 current-source verified MP3, 45 image options; teacher curriculum approval remains pending.')
