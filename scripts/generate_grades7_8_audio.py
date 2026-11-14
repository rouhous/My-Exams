#!/usr/bin/env python3
"""Create full Grade 7–8 original listening MP3 with instructions, repeats and pauses."""
import asyncio,json,pathlib,re,subprocess,tempfile,os,hashlib
import edge_tts
from mutagen.mp3 import MP3
ROOT=pathlib.Path(__file__).resolve().parents[1]
MODELS=json.loads((ROOT/'grades7-8/activities.json').read_text(encoding='utf-8'))
OUT=ROOT/'grades7-8/assets/audio-natural'
OUT.mkdir(parents=True,exist_ok=True)
VOICES=('en-GB-SoniaNeural','en-GB-RyanNeural')
MANIFEST={}
def ff(*args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
async def make(m,s):
  with tempfile.TemporaryDirectory() as d:
    tmp=pathlib.Path(d);cache={};seq=[]
    async def say(text,voice=0):
      key=(text,voice)
      if key not in cache:
        p=tmp/f'voice{len(cache):03d}.mp3'
        await edge_tts.Communicate(text,VOICES[voice],rate='-8%').save(str(p))
        if p.stat().st_size<1200:raise ValueError(f'Invalid speech {m["id"]}')
        cache[key]=p
      seq.append(cache[key])
    def pause(sec):
      p=tmp/f'pause{len(seq):03d}.mp3'
      ff('-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=44100','-t',sec,'-c:a','libmp3lame','-b:a','96k',p)
      seq.append(p)
    if s['key']=='listening1':
      await say('You are going to hear five short texts. For each text, choose the correct picture, A, B or C. You will hear the texts twice.')
      pause(3)
      for i,item in enumerate(s['items']):
        for repeat in range(2):
          await say(f'Text {i+1}. '+re.sub(r'^Text (?:one|two|three|four|five|[1-5])[. :]+','',item['script'],flags=re.I),i%2)
          pause(3)
    else:
      await say('You are going to hear a dialogue. Listen carefully and answer the questions. You will hear the dialogue twice.')
      pause(3)
      script=s.get('script') or s.get('transcript') or ''
      script=re.sub(r'^Listening two\.\s*Listen to the dialogue carefully\.\s*','',script,flags=re.I)
      chunks=re.split(r'(?=\b(?:Interviewer|Maha|Hind|Salim|Alya|Dana|Faris|Nasser|Rashid)\s*:)',script)
      speakers=[]
      for part in chunks:
        hit=re.match(r'\s*(Interviewer|Maha|Hind|Salim|Alya|Dana|Faris|Nasser|Rashid)\s*:\s*(.*)',part,flags=re.S)
        if hit and hit.group(2).strip():speakers.append((hit.group(2).strip(),0 if hit.group(1)=='Interviewer' else 1))
      if len(speakers)<4:
        speakers=[(script,1)]
      for repeat in range(2):
        for text,voice in speakers:
          await say(text,voice);pause(.55)
        pause(3)
    concat=tmp/'concat.txt'
    concat.write_text(''.join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in seq))
    out=OUT/f'{m["id"]}-{s["key"]}.mp3'
    ff('-f','concat','-safe','0','-i',concat,'-ac','1','-ar','44100','-c:a','libmp3lame','-b:a','96k',out)
    assert out.stat().st_size>15000 and MP3(out).info.length>40,out
    fp=hashlib.sha256(json.dumps({'items':s.get('items'), 'script':s.get('script'),'transcript':s.get('transcript')},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    MANIFEST[f'{m["id"]}-{s["key"]}']={'mp3':out.name,'script_and_questions_sha256':fp,'seconds':round(MP3(out).info.length,2),'bytes':out.stat().st_size,'sourceExam':m['id'],'voices':list(VOICES)}
    print('VALID',out.relative_to(ROOT),round(MP3(out).info.length),'sec',flush=True)
async def main():
  for m in MODELS:
    if os.environ.get('ONLY_GRADE') and str(m['grade'])!=os.environ['ONLY_GRADE']: continue
    for s in m['sections']:
      if s['key'] in ('listening1','listening2'):
        await make(m,s)
  (OUT/'manifest.json').write_text(json.dumps(MANIFEST,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':asyncio.run(main())
