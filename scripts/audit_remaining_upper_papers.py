#!/usr/bin/env python3
"""Strict structural/source-integrity audit: 8 new Grades 11/12 SAH-shaped unit drafts.
No outcome is a Ministry certificate or approval of educational content.
"""
import json,pathlib,hashlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'targeted_units/full_papers.json').read_text())
spec=json.loads((ROOT/'UPPER_GRADES_SAH_SEM1_2026_SPEC.json').read_text())
assert d['modelCount']==8 and len(d['papers'])==8
ids=set();stats=[]
for paper in d['papers']:
    id=paper['id'];assert id not in ids;ids.add(id)
    tr=str(paper['grade'])+'-'+paper['track']
    official=spec['tracks'][tr]
    keys=[q['id'] for q in official['sections']]
    assert paper['sectionOrder']==keys,(id,'section-order')
    assert len(paper['sections'])==len(keys) and paper['minutes']==official['minutes']
    assert paper['marks']==official['marks']==sum(paper['sections'][k]['marks'] for k in keys)
    assert paper['certifiedTextbookMatch'] is False and paper['readyForStudentExam'] is False
    for section in official['sections']:
        k=section['id'];item=paper['sections'][k]
        assert item['marks']==section['marks'],(id,k,'marks')
        if 'script' in item:
            assert item['wordCount']==len(item['script'].split())
            lo,hi=section['lengthWords'];assert lo<=item['wordCount']<=hi,(id,k,'words',item['wordCount'])
        if 'passage' in item and 'wordCount' in item:
            assert item['wordCount']==len(item['passage'].split()),(id,k,'text-words')
            if 'lengthWords' in section:
                lo,hi=section['lengthWords'];assert lo<=item['wordCount']<=hi,(id,k,'text-length',item['wordCount'])
        if 'lengthWordsEach' in section:
            lo,hi=section['lengthWordsEach']
            assert all(lo<=len(t['passage'].split())<=hi for t in item['texts']),(id,k,'short texts')
        if 'minWords' in section: assert item['minWords']>=section['minWords']
        if k.startswith('lst') and k=='lst1':assert 25<=item['speakerTurns']<=30
        for q in item.get('questions',[]):
            if isinstance(q.get('options'),list):
                assert isinstance(q['answer'],int) and 0<=q['answer']<len(q['options']),(id,k,q)
            else:assert isinstance(q.get('answer'),str) and q['answer'],(id,k,q)
    types=lambda key:[q['type'] for q in paper['sections'][key]['questions']]
    if tr=='11-elective':
        assert types('lst1')==['mc']*6+['tf']*4
        assert types('lst2')==['short']*6+['gap']*4
        assert types('rdg1')==['short']*6+['tf']*4
        assert types('rdg2')==['mc']*6+['match']*4
        assert sum(q.get('kind')=='meaning' for q in paper['sections']['rdg2']['questions'])==2
        assert paper['sections']['rdg2']['paragraphs']>=6
    else:
        assert types('lst1')==['mc']*7
        assert types('lst2')==['short']*4+['mc']*4
        assert types('grm')==['mc']*5 and all(len(q['options'])==2 for q in paper['sections']['grm']['questions'])
        assert types('vcb')==['mc']*5 and all(len(q['options'])==3 for q in paper['sections']['vcb']['questions'])
        assert types('rdg1')==['tf']*(5 if tr=='11-core' else 7)
        assert types('rdg2')==['mc']*(7 if tr=='11-core' else 8)
        assert types('rdg3')==['short']*(4 if tr=='11-core' else 6)+['mc']*4
    stats.append(dict(id=id,grade=paper['grade'],track=paper['track'],unit=paper['unit'],
      marks=paper['marks'],sections=len(keys),listening=[paper['sections'][k]['wordCount'] for k in ('lst1','lst2')]))
assert set(ids)=={'11-core-unit1','11-core-unit3','11-core-unit4','11-elective-unit3','11-elective-unit4','12-core-unit2','12-core-unit3','12-core-unit4'}
print(json.dumps({'result':'STRUCTURE_PASS__TEACHER_EDUCATIONAL_REVIEW_PENDING','paperCount':len(stats),'papers':stats},indent=2))
