#!/usr/bin/env python3
"""Grade 10 E/F source overlay for nonpublished listening audition only.

Run in a disposable GitHub Actions checkout. Do not commit resulting bank or
publish MP3s until review and all links are validated.
"""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STAGED=ROOT/'review/grade10-e-f-unique-listening.json'
BANK=ROOT/'grade10/data.json'

def validate():
    staged=json.loads(STAGED.read_text(encoding='utf-8'))
    models=staged['models']
    assert set(models)=={'E','F'}
    scripts=[]
    for key,task in models.items():
        assert len(task['questions'])==15
        assert len(task['passage'].split())>=170
        for q in task['questions']:
            assert q.get('evidence'),'Missing source evidence: '+key
            if 'options' in q:
                assert 0 <= q['answer'] < len(q['options'])
            else:
                assert isinstance(q.get('answer'),str) and q['answer'].strip()
        from sys import path
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        from listening_voice_roles import parse_dialogue
        parsed=parse_dialogue(task['passage'],task['speakerGenders'])
        assert len(parsed)>=12,(key,len(parsed))
        assert {speaker for _,_,speaker in parsed}==set(task['speakerGenders'])
        scripts.append(' '.join(task['passage'].lower().split()))
    assert len(set(scripts))==2
    existing=json.loads(BANK.read_text(encoding='utf-8'))
    old={x['id']:x['listening']['passage'] for x in existing['models']}
    assert old['E']==old['A'] and old['F']==old['D'], 'source duplicates have changed since pilot'
    assert all(script not in [' '.join(v.lower().split()) for v in old.values()] for script in scripts)
    print('STAGE validated two original Grade 10 listening passages, 30 questions and explicit cast')
    return existing,models

def main():
    arg=argparse.ArgumentParser()
    arg.add_argument('--apply',action='store_true')
    opts=arg.parse_args()
    bank,models=validate()
    if not opts.apply:
        print('DRY RUN: original bank unchanged')
        return
    for item in bank['models']:
        if item['id'] in models:
            item['listening']={'title':models[item['id']]['title'],
                               'passage':models[item['id']]['passage'],
                               'questions':models[item['id']]['questions'],
                               'speakerGenders':models[item['id']]['speakerGenders']}
            item['audioLocal']='audio/g10-'+item['id'].lower()+'-listening.mp3'
            item['listeningReviewStatus']='draft-preview-only'
    BANK.write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('STAGE overlaid models E,F only in disposable checkout')
if __name__=='__main__':
    main()
