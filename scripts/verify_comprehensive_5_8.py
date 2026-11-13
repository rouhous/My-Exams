#!/usr/bin/env python3
"""Check Grades 5–8 student exams and cross-unit mixed models against their original media."""
import json,re,pathlib,subprocess,tempfile
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
REPORT={'grades':{},'errors':[],'notes':[
 'E/F combine complete tasks from source models A-D; they are not independently new content.',
 'A-D are not yet certified to match their designated units in every section.',
 'No phone-level offline test was performed by this script.'
]}
class Inline(HTMLParser):
 def __init__(self):super().__init__();self.data=[];self.script=None
 def handle_starttag(self,tag,attrs):
  if tag=='script':
   a=dict(attrs);self.script=a
 def handle_endtag(self,tag):
  if tag=='script':self.script=None
 def handle_data(self,data):
  if self.script is not None and data.strip():
   self.data.append((self.script.get('id'),self.script.get('type'),data))
def embedded(path,id):
 content=path.read_text(encoding='utf-8')
 mark='<script type="application/json" id="'+id+'">'
 start=content.index(mark)+len(mark)
 stop=content.index('</script>',start)
 return json.loads(content[start:stop])
def jscheck(path):
 p=Inline();p.feed(path.read_text(encoding='utf-8'))
 for n,(sid,typ,script) in enumerate(p.data):
  if typ=='application/json':continue
  if not script.strip():continue
  with tempfile.NamedTemporaryFile(mode='w',suffix='.js',encoding='utf-8') as f:
   f.write(script);f.flush()
   proc=subprocess.run(['node','--check',f.name],capture_output=True,text=True)
   if proc.returncode:REPORT['errors'].append(f'{path}: script {n}: '+proc.stderr[-450:])
for grade in (5,6):
 base=ROOT/'grades5-6'
 a=json.loads((base/'activities.json').read_text())['activities']
 html=embedded(base/'index.html','bank')['activities']
 if a!=html:REPORT['errors'].append(f'G{grade} embedded HTML data differs from activities.json')
 originals=[x for x in a if x['grade']==grade and x['model'] in 'ABCD']
 keys=[(x['skill'],x['part']) for x in originals if x['model']=='A']
 for m in 'ABCD':
  parts=[x for x in originals if x['model']==m]
  if len(parts)!=8 or sum(x['marks'] for x in parts)!=40:REPORT['errors'].append(f'G{grade} model {m} malformed')
  for x in parts:
   if x['skill']=='listening':
    if not (base/x['audio']).exists():REPORT['errors'].append(f'Missing provisional MP3: {base/x["audio"]}')
    if not (base/'audio-natural'/(x['id']+'.mp3')).exists():REPORT['errors'].append(f'Missing natural MP3: {x["id"]}')
 for label,seed in [('E',1),('F',2)]:
  order='ABCD';source=[order[([0,1,2,3,2,3,0,1][i]+seed)%4] for i in range(8)]
  built=[next((x for x in originals if x['model']==source[i] and (x['skill'],x['part'])==key),None) for i,key in enumerate(keys)]
  if None in built or sum(x['marks'] for x in built)!=40 or len(set(source))!=4:REPORT['errors'].append(f'G{grade} mixed {label} malformed')
 REPORT['grades'][str(grade)]={'sourceModels':4,'fixedMixedModels':2,'randomMode':True,'sectionsPerPaper':8,'marksPerPaper':40,'naturalAudioCount':8}
for grade in (7,8):
 base=ROOT/'grades7-8'
 arr=json.loads((base/'activities.json').read_text())
 html=embedded(base/'index.html','DATA')
 if arr!=html:REPORT['errors'].append(f'G{grade} embedded HTML data differs from activities.json')
 bases=[x for x in arr if x['grade']==grade and x['model'] in 'ABCD']
 keys=['listening1','listening2','grammarvocabulary','reading1','reading2','writing1','writing2']
 for m in bases:
  if len(m['sections'])!=7 or sum(x['marks'] for x in m['sections'])!=40:REPORT['errors'].append(f'G{grade} model {m["model"]} malformed')
  for section in m['sections']:
   if section['key']=='grammarvocabulary' and (len(section['items'])!=10 or section['marks']!=10):REPORT['errors'].append(f'G{grade} model {m["model"]} invalid cloze')
   if section['key'].startswith('listening'):
    if not (base/section['audio']).exists():REPORT['errors'].append(f'G{grade}: missing backup {section["audio"]}')
    if not (base/'assets/audio-natural'/(m['id']+'-'+section['key']+'.mp3')).exists():REPORT['errors'].append(f'G{grade} missing natural {m["id"]}/{section["key"]}')
 for label,sources in [('E','ABCDABC'),('F','CDABDCA')]:
  parts=[next((s for m in bases if m['model']==sources[i] for s in m['sections'] if s['key']==key),None) for i,key in enumerate(keys)]
  if None in parts or sum(x['marks'] for x in parts)!=40 or len(set(sources))!=4:REPORT['errors'].append(f'G{grade} mixed {label} malformed')
 REPORT['grades'][str(grade)]={'sourceModels':4,'fixedMixedModels':2,'randomMode':True,'sectionsPerPaper':7,'marksPerPaper':40,'naturalAudioCount':8}
for page in ('grades5-6/index.html','grades7-8/index.html'):jscheck(ROOT/page)
path=ROOT/'docs'/'QA_G5_G8_COMPREHENSIVE.json';path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(REPORT,ensure_ascii=False,indent=2))
if REPORT['errors']:raise SystemExit(1)
