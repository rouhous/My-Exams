#!/usr/bin/env python3
"""Stage Grade 11/12 unique Listening 2 drafts only in disposable CI checkouts.

The existing approved/teacher-review sources are never modified in GitHub.
"""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DRAFT=ROOT/'review/g11-g12-core-listening2-unique-replacements.json'

def stage(apply=False):
    doc=json.loads(DRAFT.read_text(encoding='utf-8'))
    rows=doc['drafts']
    assert len(rows)==2 and {(x['grade'],x['unit']['number']) for x in rows}=={(11,4),(12,4)}
    for row in rows:
        assert row['track']=='core' and row['skill']=='listening2'
        assert row['readyForStudentExam'] is False
        assert 300<=len(row['script'].split())<=350, (row['grade'],'wrong length')
        questions=row['questions']
        assert len(questions)==8 and sum(q['type']=='short' for q in questions)==4
        assert sum(q['type']=='mc' for q in questions)==4
        for question in questions:
            assert question['evidence'].casefold() in row['script'].casefold(),question['stem']
        path=ROOT/f"grade{row['grade']}/core/units/unit4-listening2-original-draft.json"
        source=json.loads(path.read_text(encoding='utf-8'))
        assert source['unit']['number']==row['unit']['number']
        assert source['status']=='original_unit_teacher_review_draft'
        if apply:
            source.update(script=row['script'],passage=row['script'],wordCount=row['wordCount'],
                          questions=questions,readyForStudentExam=False,
                          certifiedTextbookMatch=False,audioStatus='REVIEW_ONLY_NEW_MP3_REQUIRED')
            path.write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print('OVERLAY',path.relative_to(ROOT),'words',row['wordCount'])
    if not apply:print('DRY RUN: validation only; no student source changed')
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--apply',action='store_true')
    stage(parser.parse_args().apply)
