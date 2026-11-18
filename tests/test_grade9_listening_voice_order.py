"""Grade 9: voice IDs, single-pass order, and original source data."""
import json
import pathlib
import sys
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from listening_voice_roles import parse_dialogue, voice_for_speaker, voice_for_narration
class Grade9ListeningVoiceTests(unittest.TestCase):
 def setUp(self):
  c=(ROOT/'grade9/data.js').read_text(encoding='utf-8')
  self.models={m['model']:m for m in json.loads(c.removeprefix('const EXAM_DATA=').rstrip(';\n '))['models']}
 def test_student_js_matches_audio_generator_json(self):
  js=(ROOT/'grade9/data.js').read_text(encoding='utf-8')
  browser=json.loads(js.removeprefix('const EXAM_DATA=').rstrip(';\n '))
  generator=json.loads((ROOT/'grade9/data.json').read_text(encoding='utf-8'))
  self.assertEqual(browser,generator,'Grade 9 web questions and TTS source files must be identical')
 def test_five_texts_for_each_original_fixed_model(self):
  for model in 'ABCG':
   section=next(t for t in self.models[model]['tasks'] if t['id'].endswith('L1'))
   self.assertEqual(len(section['items']),5,model)
 def test_female_alyas_are_not_male(self):
  t=next(t for t in self.models['C']['tasks'] if t['id']=='g9-C-L2')
  turns=parse_dialogue(t['transcript'])
  self.assertGreaterEqual(len(turns),6)
  self.assertEqual({voice for _,voice,name in turns if name=='Alya'},{2})
 def test_salim_and_rashid_male(self):
  for model,name in [('B','Salim'),('G','Rashid')]:
   t=next(t for t in self.models[model]['tasks'] if t['id'].endswith('L2'))
   turns=parse_dialogue(t['transcript'])
   self.assertEqual({voice for _,voice,speaker in turns if speaker==name},{1})
 def test_narrator_pronouns_do_not_override_voice(self):
  self.assertEqual(voice_for_narration('She is a good singer. I met her yesterday.',fallback_voice=1),1)
 def test_no_old_individual_repetition_pattern(self):
  src=(ROOT/'scripts/generate_grade9_audio.py').read_text()
  self.assertIn("for repetition in range(2):",src)
  self.assertIn("playback_sequence.append('now-listen-again')",src)
  self.assertIn("playback_sequence.append('text-'+labels[i])",src)
  self.assertNotIn("for i,item in enumerate(task['items']):\n            for repetition",src)
if __name__=='__main__':unittest.main()
