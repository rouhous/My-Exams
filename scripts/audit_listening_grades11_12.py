#!/usr/bin/env python3
"""Audit Grades 11–12 Core/Elective listening source for repeated content.

No AI/semantic assertions: outputs exact and phrase-level overlaps for teacher
review. Never auto-rewrite source scripts or publish a paper based on this audit.
"""
import argparse
import collections
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEAKER_LABEL = re.compile(r'(?<![A-Za-z0-9])(?:Interviewer|Presenter|Host|Guide|Adviser|Student|Teacher|Narrator|[A-Z][a-z]{2,15})\s*:\s*')
STOP_SENTENCES = {
    'now listen again', 'listen carefully and answer the questions',
    'you will hear the recording twice'
}

def clean(s):
    s = SPEAKER_LABEL.sub(' ', s or '')
    return re.sub(r'\s+', ' ', re.sub(r"[^a-z0-9 ]", ' ', s.lower())).strip()

def tokens(s):
    return clean(s).split()

def grams(seq, width):
    return set(tuple(seq[i:i+width]) for i in range(max(0,len(seq)-width+1)))

def dice_overlap(a,b):
    if not a or not b: return 0
    return 2*len(a&b)/(len(a)+len(b))

def records():
    result=[]
    for grade,track,unit,part in itertools.product((11,12),('core','elective'),range(1,5),(1,2)):
        path=ROOT/f'grade{grade}/{track}/units/unit{unit}-listening{part}-original-draft.json'
        if not path.is_file():
            raise FileNotFoundError(f'Expected script missing: {path.relative_to(ROOT)}')
        obj=json.loads(path.read_text(encoding='utf-8'))
        script=obj.get('script') or obj.get('passage')
        if not isinstance(script,str) or not script.strip():
            raise ValueError(f'Missing listening script: {path.relative_to(ROOT)}')
        rec=dict(grade=grade,track=track,unit=unit,part=part,
                 path=str(path.relative_to(ROOT)),script=script,
                 wordCount=len(tokens(script)),
                 questions=len(obj.get('questions') or []),
                 status=obj.get('status'),
                 readyForStudentExam=obj.get('readyForStudentExam'))
        rec['_t']=tokens(script)
        rec['_gram3']=grams(rec['_t'],3)
        rec['_gram6']=grams(rec['_t'],6)
        rec['_words']=set(w for w in rec['_t'] if len(w)>3)
        result.append(rec)
    return result

def audit(rows):
    repeated=[]
    for x,y in itertools.combinations(rows,2):
        exact=clean(x['script'])==clean(y['script'])
        gram3=dice_overlap(x['_gram3'],y['_gram3'])
        gram6=dice_overlap(x['_gram6'],y['_gram6'])
        shared6=x['_gram6']&y['_gram6']
        # Repeated six-word chunks may indicate templated listening texts.
        if not exact and gram3 < 0.12 and len(shared6)<4:
            continue
        repeated.append(dict(a=x['path'],b=y['path'],
            crossGrade=x['grade']!=y['grade'],
            crossTrack=x['track']!=y['track'],
            exact=exact,sharedSixWordPhrases=len(shared6),
            threeGramDice=round(gram3,3),sixGramDice=round(gram6,3),
            representativeRepeatedPhrases=[' '.join(p) for p in sorted(shared6)[:5]]))
    repeated.sort(key=lambda x:(x['exact'],x['sixGramDice'],x['threeGramDice']),reverse=True)
    groupcounts=collections.Counter(f"G{x['grade']}/{x['track']}/L{x['part']}" for x in rows)
    return {
        'scope':'Grades 11–12 Core/Elective — 4 units x 2 listening tasks each',
        'examApproved':False,
        'totalScripts':len(rows),
        'sourceCounts':dict(sorted(groupcounts.items())),
        'exactPairs':sum(r['exact'] for r in repeated),
        'highTemplateSimilarityPairs':sum(r['sixGramDice']>=0.25 for r in repeated),
        'crossGradeFlaggedPairs':sum(r['crossGrade'] for r in repeated),
        'flaggedPairs':repeated,
        'sources':[dict(path=x['path'],wordCount=x['wordCount'],questions=x['questions'],
                        status=x['status'],readyForStudentExam=x['readyForStudentExam'])
                   for x in rows],
        'note':'Overlap metrics are triage signals, not proof of identical learning outcomes. Human review needed.'
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path)
    p.add_argument('--fail-exact',action='store_true')
    args=p.parse_args()
    report=audit(records())
    assert report['totalScripts']==32, report['totalScripts']
    if args.output:
        args.output.parent.mkdir(exist_ok=True,parents=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('HIGH-GRADE LISTENING AUDIT:',report['totalScripts'],'scripts')
    print('EXACT PAIRS:',report['exactPairs'],'HIGH TEMPLATE SIMILARITY PAIRS:',report['highTemplateSimilarityPairs'])
    for f in report['flaggedPairs'][:12]:
        print('FLAG',f['a'],'vs',f['b'],'sixGram=',f['sixGramDice'],
              'triGram=',f['threeGramDice'],'crossGrade=',f['crossGrade'])
    if args.fail_exact and report['exactPairs']:
        raise SystemExit('BLOCK RELEASE: identical listening text found in Grades 11–12')
if __name__=='__main__':
    main()
