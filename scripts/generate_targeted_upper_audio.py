#!/usr/bin/env python3
"""Synthesize two read-twice local neural MP3 recordings for each newly authored upper-grade unit paper.
Do not attach an MP3 unless its exact UTF-8 text SHA matches the current source.
Runs independently for each track to avoid conflicting GitHub commits.
"""
import asyncio,hashlib,json,pathlib,re,subprocess,sys,tempfile
from mutagen.mp3 import MP3
import edge_tts
ROOT=pathlib.Path(__file__).resolve().parents[1]
BANK=json.loads((ROOT/'targeted_units/full_papers.json').read_text())
TRACK=sys.argv[1] if len(sys.argv)>1 else None
assert TRACK in ('11-core','11-elective','12-core'),"usage: generate_targeted_upper_audio.py 11-core|11-elective|12-core"
OUT=ROOT/'targeted_units/audio'/TRACK
OUT.mkdir(parents=True,exist_ok=True)
VOICES=('en-GB-SoniaNeural','en-GB-RyanNeural')
def ff(*args):
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
async def render(script,track,skill,target):
 with tempfile.TemporaryDirectory() as d:
  tmp=pathlib.Path(d);chunks=[];cache={}
  async def speak(txt,voice):
   txt=re.sub(r'\s+',' ',txt).strip()
   if not txt:return
   key=(txt,voice)
   if key not in cache:
    dest=tmp/f'v{len(cache):03d}.mp3'
    for attempt in range(4):
     try:
      await edge_tts.Communicate(txt,VOICES[voice],rate='-8%').save(str(dest))
      if dest.stat().st_size<1500:raise ValueError('Tiny neural recording')
      break
     except Exception as e:
      if attempt==3:raise
      print('RETRY',str(e)[:90],flush=True)
      await asyncio.sleep(attempt*2+2)
    cache[key]=dest
   chunks.append(cache[key])
  def pause(seconds):
   p=tmp/f'p{len(chunks):03d}.mp3'
   ff('-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=44100','-t',str(seconds),'-c:a','libmp3lame','-b:a','96k',p)
   chunks.append(p)
  intro='You will hear a recording about '+track.replace('-',' ')+' unit skills. Listen carefully and answer the questions. The recording will be played twice.'
  await speak(intro,0);pause(3)
  if skill=='lst1':
   passages=[]
   for l in script.splitlines():
    m=re.fullmatch(r'(Interviewer|Student):\s*(.+)',l.strip())
    if not m:raise ValueError('Invalid two-voice line: '+l[:150])
    passages.append((m.group(2),0 if m.group(1)=='Interviewer' else 1))
   if not 25<=len(passages)<=30:raise ValueError('Dialogue must have 25-30 turns')
  else:
   passages=[(x.strip().replace('\n',' '),0) for x in re.split(r'\n\s*\n',script) if x.strip()]
   if not passages:raise ValueError('Empty single-voice text')
  for repetition in range(2):
   for txt,voice in passages:
    await speak(txt,voice)
    pause(.5 if skill=='lst1' else 1.0)
   pause(6 if repetition==0 else 2)
  concat=tmp/'list.txt'
  concat.write_text(''.join("file '"+str(x.resolve()).replace("'","'\\''")+"'\n" for x in chunks))
  ff('-f','concat','-safe','0','-i',concat,'-ac','1','-ar','44100','-c:a','libmp3lame','-b:a','96k',target)
 duration=MP3(target).info.length
 if target.stat().st_size<25000 or duration<150:raise ValueError('Audio is too short: '+str(target))
 return round(duration,2)
async def main():
 old=OUT/'manifest.json'
 previous=json.loads(old.read_text()) if old.exists() else {}
 manifest={}
 papers=[p for p in BANK['papers'] if str(p['grade'])+'-'+p['track']==TRACK]
 assert len(papers) in (2,3),len(papers)
 for p in papers:
  for skill in ('lst1','lst2'):
   task=p['sections'][skill]
   script=task['script']
   assert len(script.split())==task['wordCount']
   source=hashlib.sha256(script.encode('utf-8')).hexdigest()
   ident=p['id']+'-'+skill
   name=ident+'.mp3';target=OUT/name
   expected=list(VOICES) if skill=='lst1' else [VOICES[0]]
   oldrec=previous.get(ident,{})
   if (oldrec.get('scriptSha256')==source and oldrec.get('voices')==expected
       and target.is_file() and target.stat().st_size>25000 and MP3(target).info.length>150):
    duration=round(MP3(target).info.length,2)
    print('REUSE',name,flush=True)
   else:
    print('SPEAKING',ident,flush=True)
    duration=await render(script,TRACK,skill,target)
   manifest[ident]=dict(paperId=p['id'],skill=skill,mp3=name,
    scriptSha256=source,durationSeconds=duration,
    bytes=target.stat().st_size,voices=expected,
    scriptReadTwice=True,status='generated_neural_audio__teacher_listening_review_pending')
   print('VALID',ident,duration,'s',flush=True)
 old.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print('TRACK COMPLETE',TRACK,len(manifest),'files')
if __name__=='__main__':asyncio.run(main())
