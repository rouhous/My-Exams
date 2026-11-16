#!/usr/bin/env python3
"""Audit repeated My Exams listening scripts without changing scripts or MP3s.

Usage: python scripts/audit_listening_reuse.py --max-exact=38 --fail-cross-grade
The current baseline is 38 *additional occurrences*, not 38 MP3 files.
Remove this compatibility budget as duplicated models are rewritten.
"""
import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def normalize(s):
    s = re.sub(r'\b(?:Text|Dialogue)\s+(?:one|two|three|four|five|[1-5])\s*[.:]\s*', '', s, flags=re.I)
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9\s]', ' ', s.lower())).strip()


def records():
    result = []
    def add(grade, model, task, kind, text, source, item=None):
        if not isinstance(text, str) or len(text.split()) < 8:
            return
        result.append(dict(grade=grade, model=str(model), task=task,
                           kind=kind, source=source, item=item,
                           text=text.strip(), normalized=normalize(text)))

    source = 'grades5-6/activities.json'
    doc = json.loads((ROOT / source).read_text(encoding='utf-8'))
    for task in doc['activities']:
        if task['skill'] != 'listening':
            continue
        for i, text in enumerate(task.get('passages') or [], 1):
            add(task['grade'], task['model'], task['id'], 'short', text, source, i)
        add(task['grade'], task['model'], task['id'], 'full', task.get('passage'), source)

    source = 'grades7-8/activities.json'
    models = json.loads((ROOT / source).read_text(encoding='utf-8'))
    for model in models:
        for section in model['sections']:
            if section['key'] == 'listening1':
                for i, item in enumerate(section['items'], 1):
                    add(model['grade'], model['model'], model['id'] + '-listening1',
                        'short', item['script'], source, i)
            elif section['key'] == 'listening2':
                add(model['grade'], model['model'], model['id'] + '-listening2',
                    'full', section.get('script') or section.get('transcript'), source)

    for source in ('grade9/data.js', 'grade9/unit-exams/models.json'):
        raw = (ROOT / source).read_text(encoding='utf-8')
        if source.endswith('.js'):
            raw = raw.removeprefix('const EXAM_DATA=').rstrip(';\n ')
        doc = json.loads(raw)
        for model in doc['models']:
            for task in model['tasks']:
                if task['skill'] != 'listening':
                    continue
                scripted = [item for item in task.get('items', []) if item.get('script')]
                if scripted:
                    for i, item in enumerate(scripted, 1):
                        add(9, model['model'], task['id'], 'short', item['script'], source, i)
                else:
                    add(9, model['model'], task['id'], 'full',
                        task.get('transcript'), source)

    source = 'grade10/data.json'
    doc = json.loads((ROOT / source).read_text(encoding='utf-8'))
    for model in doc['models']:
        section = model.get('listening') or {}
        add(10, model['id'], model['id'] + '-listening', 'full',
            section.get('passage') or section.get('script') or section.get('transcript'),
            source)
    return result


def audit(rows):
    groups = collections.defaultdict(list)
    by_grade = collections.Counter()
    for row in rows:
        groups[row['normalized']].append(row)
        by_grade[str(row['grade'])] += 1
    repeated = [items for items in groups.values() if len(items) > 1]
    repeated.sort(key=lambda items: (items[0]['grade'], items[0]['task'], items[0].get('item') or 0))
    details = []
    cross_grade = []
    counts = collections.Counter()
    for items in repeated:
        occurrence = len(items) - 1
        involved = {str(item['grade']) for item in items}
        for grade in involved:
            counts[grade] += len([item for item in items if str(item['grade']) == grade]) - 1
        summary = {
            'additionalOccurrences': occurrence,
            'gradeGroups': sorted(involved),
            'reusedIn': [
                {'grade': i['grade'], 'model': i['model'], 'task': i['task'],
                 'item': i['item'], 'source': i['source']} for i in items
            ],
            'sample': items[0]['text'][:120]
        }
        details.append(summary)
        if len(involved) > 1:
            cross_grade.append(summary)
    return {
        'scannedSegments': len(rows),
        'uniqueScripts': len(groups),
        'exactDuplicateGroups': len(repeated),
        'additionalExactOccurrences': sum(x['additionalOccurrences'] for x in details),
        'sourceSegmentsByGrade': dict(sorted(by_grade.items())),
        'extraOccurrencesByGrade': dict(sorted(counts.items())),
        'crossGradeExactGroups': len(cross_grade),
        'duplicates': details
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=pathlib.Path)
    parser.add_argument('--max-exact', type=int, default=-1,
                        help='Fail only if count grows above existing baseline')
    parser.add_argument('--fail-cross-grade', action='store_true')
    args = parser.parse_args()
    report = audit(records())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Listening inventory: {scannedSegments} segments, {uniqueScripts} distinct, '
          '{additionalExactOccurrences} extra occurrences, {crossGradeExactGroups} cross-grade groups'.format(**report))
    print('Extra by grade:', report['extraOccurrencesByGrade'])
    if args.max_exact >= 0 and report['additionalExactOccurrences'] > args.max_exact:
        raise SystemExit('FAIL: new exact duplicates exceed allowed review baseline')
    if args.fail_cross_grade and report['crossGradeExactGroups']:
        raise SystemExit('FAIL: identical listening scripts across grades')
    print('Audit complete. Existing duplicates remain to be rewritten; no source changed.')


if __name__ == '__main__':
    main()
