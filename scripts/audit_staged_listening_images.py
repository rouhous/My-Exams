#!/usr/bin/env python3
"""Audit planned My Exams black-and-white image options for repeated/missing art.

Run with --require-files only on a release candidate after images are imported.
The default validates all staged plans and writes the upload checklist.
"""
import argparse,collections,json
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
    assert raw.startswith('images/') and raw.endswith('.png')
    candidates.append({'grade':9,'model':paper['model'],'task':paper['listening1']['id'],'question':q,'choice':choice,'id':Path(raw).stem,'path':'grade9/'+raw})
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
