"""Guard Listening 1 option images: letters above; never reveal option names below."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]

class ListeningPictureLayout(unittest.TestCase):
 def test_grade5_6_letter_above(self):
  s=(ROOT/"grades5-6/index.html").read_text(encoding="utf-8")
  f=s[s.index("function pics("):s.index("function renderActivities()")]
  self.assertIn('class="picture-letter"',f)
  self.assertLess(f.index('class="picture-letter"'),f.index("<img"))
  self.assertNotIn("<small>",f)
  self.assertNotIn("</small>",f)
 def test_grade7_8_letters_above(self):
  s=(ROOT/"grades7-8/index.html").read_text(encoding="utf-8")
  f=s[s.index("q.images.map((p,j)=>"):][:520]
  self.assertLess(f.index("<b>"),f.index("<img"))
  self.assertLess(f.index("<img"),f.index("<input"))
  self.assertNotIn("q.options[j]",f)
 def test_grade9_letter_above(self):
  s=(ROOT/"grade9/index.html").read_text(encoding="utf-8")
  f=s[s.index("q.images.map((img,j)=>"):][:650]
  self.assertLess(f.index('class="picture-letter"'),f.index("<img"))
  self.assertLess(f.index("<img"),f.index('<input type="radio"'))
  self.assertIn('aria-label="Option',f)
  self.assertNotIn("q.choices[j]",f)
 def test_no_image_filename_as_label(self):
  for name in ("grades5-6/index.html","grades7-8/index.html","grade9/index.html"):
   s=(ROOT/name).read_text(encoding="utf-8")
   self.assertNotIn("data-caption",s)

if __name__=="__main__": unittest.main()
