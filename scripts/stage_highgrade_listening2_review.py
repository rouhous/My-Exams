#!/usr/bin/env python3
"""Apply six staged Grade 11/12 Core listening rewrites in CI only.

Never commit the modified source bank or release stale audio alongside new text.
"""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DRAFTS=[
 ROOT/'review/g11-g12-core-listening2-unique-replacements.json',
 ROOT/'review/g11-g12-core-remaining-listening-unique.json',
]

def run(apply=False):
    rows=[]
    for file in DRAFTS:
        obj=json.loads(file.read_text(encoding='utf-8'))
        assert obj['reviewOnly'] is True
        rows.extend(obj['drafts'])
    expected={(11,4,2),(12,4,2),(11,3,1),(11,4,1),(11,3,2),(12,4,1)}
    unit_number=lambda x: x['unit']['number'] if isinstance(x['unit'],dict) else int(x['unit'])
    part_number=lambda x: int(x['part']) if 'part' in x else int(re.search(r'\d+',x['skill']).group())
    assert {(x['grade'],unit_number(x),part_number(x)) for x in rows}==expected
    for row in rows:
        grade,unit=row['grade'],unit_number(row)
        part=part_number(row)
        assert row.get('track','core')=='core' and row['readyForStudentExam'] is False
        n=len(row['script'].split())
        lower,upper=(250,380) if part==1 else (300,350)
        assert lower<=n<=upper,(grade,unit,part,n)
        questions=row['questions']
        assert len(questions)==(7 if part==1 else 8)
        if part==2:
            assert sum(q['type']=='short' for q in questions)==4
            assert sum(q['type']=='mc' for q in questions)==4
        else:
            assert all(q['type']=='mc' for q in questions)
        for q in questions:
            assert q['evidence'].lower() in row['script'].lower(),(grade,unit,part,q['stem'])
        path=ROOT/f'grade{grade}/core/units/unit{unit}-listening{part}-original-draft.json'
        current=json.loads(path.read_text(encoding='utf-8'))
        assert current['unit']['number']==unit
        assert current['status']=='original_unit_teacher_review_draft'
        if part==1:
            labels=re.findall(r'(?m)^([A-Z][A-Za-z]+):',row['script'])
            assert 24<=len(labels)<=30,(grade,unit,len(labels))
            assert set(labels)==set(row['cast']),(grade,unit,'speaker mismatch')
        if apply:
            current.update(script=row['script'],passage=row['script'],wordCount=n,
                           questions=questions,readyForStudentExam=False,
                           certifiedTextbookMatch=False,audioStatus='REVIEW_ONLY_NEW_MP3_REQUIRED')
            if part==1:current.update(speakerTurns=len(labels),speakerGenders=row['cast'])
            path.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print('OVERLAY',path.relative_to(ROOT),'words',n)
    if not apply:print('DRY RUN: validated',len(rows),'drafts; no original files changed')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--apply',action='store_true')
    run(parser.parse_args().apply)
