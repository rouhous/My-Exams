"""Offline, no-TTS tests: voice identity must match the named speaker.

Run: python -m unittest discover -s tests -p test_listening_voice_roles.py
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from listening_voice_roles import (
    VOICE_NAMES, KNOWN_GENDERS, parse_dialogue,
    voice_for_narration, voice_for_speaker,
)


class TestListeningVoiceRoles(unittest.TestCase):
    def test_explicit_female_interviewer_keeps_presenter_voice(self):
        self.assertEqual(voice_for_speaker("Interviewer", {"Interviewer": "female"}), 0)
        self.assertEqual(voice_for_speaker("Interviewer", {"Interviewer": "male"}), 1)
        dialog = parse_dialogue("Interviewer: Hello. Huda: Hello!", {"Interviewer": "female", "Huda": "female"})
        self.assertEqual([voice for _,voice,_ in dialog], [0,2])

    def test_named_boys(self):
        for name in ("Sam", "Hamad", "Ahmed", "Salim", "Faris", "Yousuf", "Bilal"):
            self.assertEqual(voice_for_speaker(name), 1, name)

    def test_named_girls(self):
        for name in ("Salma", "Mariam", "Fatma", "Dana", "Alya", "Maha", "Hind", "Noura"):
            self.assertEqual(voice_for_speaker(name), 2, name)

    def test_voices_are_different_for_female_host_and_guest(self):
        self.assertNotEqual(VOICE_NAMES[0], VOICE_NAMES[2])
        turns = parse_dialogue("Interviewer: Hello, Sam. Sam: Hello. Interviewer: And Salma? Salma: Hi!")
        self.assertEqual([turn[1] for turn in turns], [0, 1, 0, 2])

    def test_third_person_pronouns_do_not_change_narrator_gender(self):
        self.assertEqual(voice_for_narration("I met Sam. He was with his sister."), 0)
        self.assertEqual(voice_for_narration("I met Sarah. She told me her story.", fallback_voice=1), 1)
        self.assertEqual(voice_for_narration("My name is Sam. I visited the museum."), 1)
        self.assertEqual(voice_for_narration("My name is Salma. I visited the museum."), 0)
        self.assertEqual(voice_for_narration("I'm a boy, and I like science."), 1)

    def test_unknown_named_speaker_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unmapped speaker"):
            voice_for_speaker("SomeoneUnknown")
        self.assertEqual(voice_for_speaker("SomeoneUnknown", {"SomeoneUnknown": "female"}), 2)

    def test_real_grade_5_6_interviews(self):
        doc = json.loads((ROOT / "grades5-6/activities.json").read_text(encoding="utf-8"))
        tasks = [t for t in doc["activities"] if t["skill"] == "listening" and t["part"] == 2]
        self.assertEqual(len(tasks), 8)
        for task in tasks:
            with self.subTest(task=task["id"]):
                turns = parse_dialogue(task["passage"], task.get("speakerGenders"))
                self.assertGreaterEqual(len(turns), 5)
                for _, voice, speaker in turns:
                    if speaker.lower() == "interviewer":
                        self.assertEqual(voice, 0)
                    elif KNOWN_GENDERS[speaker.lower()] == "male":
                        self.assertEqual(voice, 1)
                    else:
                        self.assertEqual(voice, 2)

    def test_real_grade_7_8_interviews(self):
        models = json.loads((ROOT / "grades7-8/activities.json").read_text(encoding="utf-8"))
        self.assertEqual(len(models), 8)
        for model in models:
            section = next(s for s in model["sections"] if s["key"] == "listening2")
            with self.subTest(model=model["id"]):
                turns = parse_dialogue(section["script"], section.get("speakerGenders"))
                self.assertGreaterEqual(len(turns), 4)
                for _, voice, speaker in turns:
                    self.assertEqual(voice, voice_for_speaker(speaker))

    def test_unnamed_dialogue_keeps_distinct_roles(self):
        turns = parse_dialogue("A: Which telescope? B: This one. A: Thank you.")
        self.assertEqual([voice for _, voice, _ in turns], [0, 1, 0])


if __name__ == "__main__":
    unittest.main()
