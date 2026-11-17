#!/usr/bin/env python3
"""Audit planned My Exams black-and-white image options for repeated/missing art.

Run with --require-files only on a release candidate after images are imported.
The default validates all staged plans and writes the upload checklist.
"""
import argparse,collections,json,hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
G68=ROOT/'review/listening-replacements-grade6-8-model-d.json'
G9=[ROOT/f'review/grade9-model-{m}-original-listening.json' for m in 'def']
def inventory():
 candidates=[]
 data=json.loads(G68.read_text(encoding='utf-8'))
 for draft in data['replacements']:
  if draft['grade']==6 and draft['part']==1:
   for i,image in enumerate(draft['pictureOptions']):
    candidates.append({'grade':6,'task':draft['id'],'choice':i,'id':image,'path':f'grades5-6/images/{image}.png'})
  if draft['grade'] in (7,8) and draft['section']=='listening1':
   for q,question in enumerate(draft['items'],1):
    for choice,image in enumerate(question['images']):
     candidates.append({'grade':draft['grade'],'task':draft['id'],'question':q,'choice':choice,'id':image,'path':f'grades7-8/assets/illustrations/{image}.png'})
 for file in G9:
  paper=json.loads(file.read_text(encoding='utf-8'))
  for q,question in enumerate(paper['listening1']['items'],1):
   for choice,raw in enumerate(question['images']):
    # Review JSON uses bare IDs in Models D/E/F, while the student UI
    # consumes images/<id>.png after the disposable source overlay.
    relative = raw if raw.startswith('images/') else 'images/' + raw
    if not relative.endswith('.png'):
     relative += '.png'
    candidates.append({'grade':9,'model':paper['model'],'task':paper['listening1']['id'],'question':q,'choice':choice,'id':Path(relative).stem,'path':'grade9/'+relative})
 return candidates

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--output',type=Path,default=None)
 parser.add_argument('--require-files',action='store_true')
 args=parser.parse_args()
 pictures=inventory()
 assert len(pictures)==81,('Wrong expected image count',len(pictures))
 by_id=collections.defaultdict(list)
 for item in pictures:by_id[item['id']].append(item)
 repeated={key:items for key,items in by_id.items() if len(items)>1}
 if repeated:
  raise ValueError('Image identifiers reused in different questions: '+str(list(repeated)[:12]))
 by_grade=collections.Counter(str(q['grade']) for q in pictures)
 missing=[p for p in pictures if not (ROOT/p['path']).is_file()]
 # When a binary has been uploaded, require an exact match with the reviewed
 # picture content. Missing images are still reported as release blockers.
 integrity={}
 for spec in ('review/grade8-model-d-image-integrity.json',
              'review/grade9-model-d-image-integrity.json'):
  review=json.loads((ROOT/spec).read_text(encoding='utf-8'))
  for entry in review['items']:
   path=ROOT/entry['relativePath']
   integrity[entry['relativePath']]=entry['sha256']
 mismatches=[]
 bad_dimensions=[]
 for item in pictures:
  image=ROOT/item['path']
  if not image.is_file():continue
  blob=image.read_bytes()
  expected=integrity.get(item['path'])
  if expected and hashlib.sha256(blob).hexdigest()!=expected:
   mismatches.append(item['path'])
  if len(blob)<24 or blob[:8]!=b'\x89PNG\r\n\x1a\n':
   bad_dimensions.append(item['path'])
  else:
   width,height=struct.unpack('>II',blob[16:24])
   if (width,height)!=(512,512):bad_dimensions.append(item['path'])
 if mismatches or bad_dimensions:
  raise ValueError('Unapproved modified art or invalid 512px PNG: '+str(mismatches+bad_dimensions))
 result={'totalPlanned':len(pictures),'uniqueIdentifiers':len(by_id),
  'byGrade':dict(by_grade),'duplicateIdentifiers':0,'missingInGitHubReview':len(missing),
  'readyForLiveLinking':len(missing)==0,'imageSpecification':'2D detailed B&W cartoon; square consistent framing; no labels',
  'images':pictures,'missing':missing}
 if args.output:
  args.output.parent.mkdir(exist_ok=True,parents=True)
  args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('IMAGE QA',len(pictures),'distinct IDs; missing artwork files:',len(missing),'byGrade',dict(by_grade))
 if args.require_files and missing:
  raise SystemExit('BLOCK RELEASE: cannot link unuploaded pictures to listening questions')
 print('Review inventory complete. Missing files are a release blocker.')
if __name__=='__main__':main()
