#!/usr/bin/env python3
"""Apply staged My Exams listening replacements to a disposable CI checkout only.

This script modifies source JSON when invoked with --apply. Run only in a
throwaway runner/worktree for MP3 preview; do NOT commit edited bank files until
the recordings, unique illustrations, and answers are approved.
"""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'review/listening-replacements-grade6-8-model-d.json'


def find_section(model, key):
    found = [s for s in model['sections'] if s['key'] == key]
    if len(found) != 1:
        raise ValueError('Missing or duplicated section: '+model['id']+'/'+key)
    return found[0]


def validate(drafts):
    assert drafts['reviewOnly'] is True
    rep = drafts['replacements']
    assert {r['id'] for r in rep} == {
        'g6-d-listening-1', 'g6-d-listening-2', 'g7-d-listening1',
        'g7-d-listening2', 'g8-d-listening1', 'g8-d-listening2'
    }
    image_ids = []
    for r in rep:
        if r['grade'] == 6:
            assert len(r['questions']) == 5 and r['part'] in (1, 2)
            if r['part'] == 1:
                assert len(r['passages']) == 5
                assert len(r['pictureOptions']) == 6
                assert {x['answer'] for x in r['questions']} <= set(range(6))
                assert len({x['answer'] for x in r['questions']}) == 5
                image_ids.extend(r['pictureOptions'])
            else:
                assert len(r['passage'].split()) >= 120
                assert all(0 <= q['answer'] < len(q['options']) for q in r['questions'])
        else:
            assert len(r['items']) == 5
            if r['section'] == 'listening1':
                assert all(len(x['options']) == len(x['images']) == 3 and len(x['script'].split()) >= 25 for x in r['items'])
                assert all(0 <= x['answer'] < 3 for x in r['items'])
                image_ids.extend(img for item in r['items'] for img in item['images'])
            else:
                assert r['script'].count('Interviewer:') >= 4
                assert all(isinstance(x['answer'], bool) for x in r['items'])
    assert len(image_ids) == len(set(image_ids)), 'Image ID was repeated in newly staged review materials'
    print('STAGE validated',len(rep),'replacements,',len(image_ids),'distinct illustration IDs')


def apply(drafts):
    g56_path = ROOT / 'grades5-6/activities.json'
    g78_path = ROOT / 'grades7-8/activities.json'
    g56 = json.loads(g56_path.read_text(encoding='utf-8'))
    g78 = json.loads(g78_path.read_text(encoding='utf-8'))
    ids = {x['id']:x for x in g56['activities']}
    models = {x['id']:x for x in g78}
    for draft in drafts['replacements']:
        if draft['grade'] == 6:
            current = ids[draft['id']]
            assert current['model'] == 'D' and current['grade'] == 6
            keys = ['passages','passage','questions','pictureOptions']
            for key in keys:
                current.pop(key, None)
                if key in draft:
                    current[key] = copy.deepcopy(draft[key])
            current['unitTheme'] = draft['unitTheme']
            current['title'] = draft['title']
            current['audio'] = 'audio/' + current['id'] + '.mp3'
            current['mediaId'] = current['id']
            for copied in ('sourceModel', 'sourceActivityId'):
                current.pop(copied, None)
            current['audioStatus'] = 'draft-preview-only'
        else:
            grade = draft['grade']
            model = models[f'g{grade}-d']
            section = find_section(model,draft['section'])
            assert model['grade'] == grade and model['model'] == 'D'
            for key in ('items','script','transcript'):
                section.pop(key, None)
            section['items'] = copy.deepcopy(draft['items'])
            if draft['section']=='listening1':
                section['transcript'] = ('Listening one. You will hear five short texts twice. '
                    + ' '.join(f'Text {i+1}. {item["script"]}' for i,item in enumerate(section['items'])))
            else:
                section['script'] = draft['script']
                section['transcript'] = ('Listening two. Listen to the dialogue carefully. '
                    + ' '.join(draft['script'].split()))
            section['instructions'] = draft['instructions']
            section['audio'] = f'assets/audio/g{grade}-d-{draft["section"]}.mp3'
            section['audioStatus'] = 'draft-preview-only'
            for copied in ('sourceModel','sourceExamId'):
                section.pop(copied,None)
    g56_path.write_text(json.dumps(g56,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    g78_path.write_text(json.dumps(g78,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('STAGE sources overlaid in temporary checkout: G6D/G7D/G8D')
    return g56_path, g78_path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--apply',action='store_true',
                        help='Replace source banks ONLY in a disposable runner checkout.')
    args=parser.parse_args()
    drafts=json.loads(REVIEW.read_text(encoding='utf-8'))
    validate(drafts)
    if args.apply:
        apply(drafts)
    else:
        print('DRY RUN: no source bank changes')


if __name__=='__main__':
    main()
