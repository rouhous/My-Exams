"""Speaker-cast inventory checks for Grade 9–12 source texts (not an MP3 listening test)."""
import json
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from listening_voice_roles import KNOWN_GENDERS, SPEAKER_RE, SELF_NAME_RE, voice_for_speaker, voice_for_narration

GENERIC_ROLES = {
    'interviewer', 'host', 'presenter', 'teacher', 'student',
    'guide', 'engineer', 'counsellor', 'adviser', 'narrator', 'a', 'b'
}

def check_named_speakers(testcase, script, source):
    tags = list(SPEAKER_RE.finditer(script))
    # A colon in ordinary narration ("students reported different results: ...")
    # is NOT a new speaker. Only explicit cast labels identify characters.
    dialogue_present = any(
        tag.group(1).lower() in GENERIC_ROLES | KNOWN_GENDERS.keys()
        for tag in tags
    )
    for tag in tags:
        name = tag.group(1).lower()
        if name in GENERIC_ROLES:
            continue  # "Student" and "Adviser" need editorial casting.
        if name not in KNOWN_GENDERS:
            prefix = script[:tag.start()].rsplit('\n', 1)[-1].strip()
            if not dialogue_present or prefix:
                continue  # e.g. "different results: some preferred ..."
            testcase.fail(source + ': unknown named speaker label ' + name)
        expected = 1 if KNOWN_GENDERS[name] == 'male' else 2
        testcase.assertEqual(voice_for_speaker(name), expected, source + ': ' + name)
    self_id = SELF_NAME_RE.search(script)
    if self_id and self_id.group(1).lower() in KNOWN_GENDERS:
        expected = 1 if KNOWN_GENDERS[self_id.group(1).lower()] == 'male' else 0
        testcase.assertEqual(voice_for_narration(script), expected, source)


class TestHighGradeSpeakerSources(unittest.TestCase):
    def test_grade9_fixed_models(self):
        raw = (ROOT / 'grade9/data.js').read_text(encoding='utf-8')
        data = json.loads(raw.removeprefix('const EXAM_DATA=').rstrip(';\n '))
        for model in data['models']:
            for task in model['tasks']:
                if task['skill'] == 'listening' and task.get('group') == 2:
                    check_named_speakers(self, task.get('transcript', ''), model['model'])

    def test_grade9_unit_models(self):
        data = json.loads((ROOT / 'grade9/unit-exams/models.json').read_text(encoding='utf-8'))
        for model in data['models']:
            for task in model['tasks']:
                if task['skill'] == 'listening' and task.get('group') == 2:
                    check_named_speakers(self, task.get('transcript', ''), model['model'])

    def test_grade10_actor_labels(self):
        data = json.loads((ROOT / 'grade10/data.json').read_text(encoding='utf-8'))
        for model in data['models']:
            check_named_speakers(self, model['listening']['passage'], model['id'])

    def test_grade11_and_12_all_units(self):
        checked = 0
        for grade in (11, 12):
            for track in ('core', 'elective'):
                for unit in range(1, 5):
                    for part in (1, 2):
                        file = ROOT / f'grade{grade}/{track}/units/unit{unit}-listening{part}-original-draft.json'
                        data = json.loads(file.read_text(encoding='utf-8'))
                        check_named_speakers(self, data.get('script') or data.get('passage') or '', str(file.relative_to(ROOT)))
                        checked += 1
        self.assertEqual(checked, 32)


if __name__ == '__main__':
    unittest.main()
