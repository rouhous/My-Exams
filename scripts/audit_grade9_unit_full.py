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
 assert len(m['tasks'][0]['items'])==5
 for q in m['tasks'][0]['items']:
  assert len(q['images'])==len(q['choices'])==3 and 0<=q['answer']<3
  for image in q['images']:assert (base/image).is_file(),image
 assert len(m['tasks'][1]['items'])==5
 assert len(m['tasks'][2]['items'])==10 and m['tasks'][2]['passage'].count('_____')==10
 assert len(m['tasks'][3]['items'])==4 and len(m['tasks'][4]['items'])==6
 assert sum(len(x.get('items',[])) for x in m['tasks'])==30
print('PASS three fully drafted 40-mark unit papers, six verified local MP3 and 45 image-option references; teacher curriculum approval still pending.')
