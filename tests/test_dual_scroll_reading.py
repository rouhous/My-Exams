"""Static regression checks for dual-scroll reading and cloze layouts."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class DualScrollReadingTests(unittest.TestCase):
 def test_scrolling_panels_support_desktop_and_mobile(self):
  css=(ROOT/'shared/reading-split.css').read_text(encoding='utf-8')
  self.assertIn('grid-template-columns:minmax(0,1fr) minmax(0,1fr)',css)
  self.assertIn('overflow-y:auto',css)
  self.assertIn('@media(max-width:700px)',css)
  self.assertIn('grid-template-columns:minmax(0,1fr)',css)
  self.assertIn('@media print',css)
 def test_original_answer_inputs_are_moved_not_cloned(self):
  js=(ROOT/'shared/reading-split.js').read_text(encoding='utf-8')
  self.assertIn('reference.append(source)',js)
  self.assertIn('exercise.append(question)',js)
  self.assertNotIn('cloneNode(',js)
  self.assertIn('section.dataset.dualReady="yes"',js)
  self.assertIn('MutationObserver',js)
  self.assertIn('tabIndex=0',js)
 def test_pages_have_correct_assets(self):
  pages=[
    'grades5-6/index.html','grades7-8/index.html','grade9/index.html',
    'grade9/unit-exams/index.html','grade10/index.html','upper-grades-practice.html',
    'mixed-exams/index.html','targeted_units/index.html',
  ]+[f'grade{grade}/{track}/units/paper-{m}-preview.html'
    for grade,track,letters in ((11,'core','abcd'),(11,'elective','abcd'),(12,'core','abcd'),(12,'elective','a'))
    for m in letters]
  for item in pages:
   path=ROOT/item
   self.assertTrue(path.is_file(),item)
   html=path.read_text(encoding='utf-8')
   prefix='../'*(len(path.relative_to(ROOT).parts)-1)
   self.assertIn(prefix+'shared/reading-split.css',html,item)
   self.assertIn(prefix+'shared/reading-split.js',html,item)
 def test_g7_g8_wrap_the_tasks_that_need_split(self):
  html=(ROOT/'grades7-8/index.html').read_text(encoding='utf-8')
  self.assertIn("k.startsWith('reading')",html)
  self.assertIn("match.matching",html)
  self.assertNotIn(".single-scroll-exam .exam-dual-panel{",html)

if __name__=='__main__':unittest.main()
