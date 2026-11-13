#!/usr/bin/env python3
"""Grade 5 and 6: natural MP3 with Ministry-style instructions and pauses."""
import asyncio,json,pathlib,re,subprocess,tempfile
import edge_tts
from mutagen.mp3 import MP3
ROOT=pathlib.Path(__file__).resolve().parents[1]
TASKS=json.loads((ROOT/'grades5-6/activities.json').read_text(encoding='utf-8'))['activities']
OUT=ROOT/'grades5-6/audio-natural'
OUT.mkdir(parents=True,exist_ok=True)
VOICES=('en-GB-SoniaNeural','en-GB-RyanNeural')
def ff(*args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
async def make(task):
  with tempfile.TemporaryDirectory() as d:
    temp=pathlib.Path(d);cache={};parts=[]
    async def speak(text,voice=0):
      text=re.sub(r'\s+',' ',text).strip()
      if not text:return
      key=(text,voice)
      if key not in cache:
        f=temp/f'voice{len(cache):03d}.mp3'
        await edge_tts.Communicate(text,VOICES[voice],rate='-10%').save(str(f))
        assert f.stat().st_size>1500,f
        cache[key]=f
      parts.append(cache[key])
    def pause(sec):
      f=temp/f'pause{len(parts):03d}.mp3'
      ff('-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=44100','-t',sec,'-c:a','libmp3lame','-b:a','96k',f)
      parts.append(f)
    if task['part']==1:
      await speak('You are going to hear five short dialogues. For each dialogue, choose the correct picture. You will hear the dialogues twice.')
      pause(3)
      for i,dialogue in enumerate(task['passages']):
        turns=re.split(r'(?=\b[AB]\s*:)',dialogue)
        parsed=[]
        for p in turns:
          m=re.match(r'\s*([AB])\s*:\s*(.+)',p,flags=re.S)
          if m:parsed.append((m.group(2).strip(),0 if m.group(1)=='A' else 1))
        if not parsed:parsed=[(dialogue,0)]
        for repeat in range(2):
          await speak(f'Dialogue {i+1}.')
          for text,voice in parsed:
            await speak(text,voice);pause(.5)
          pause(3)
    else:
      await speak('You are going to hear a dialogue or interview. Listen carefully and choose the correct answers. You will hear it twice.')
      pause(3)
      passage=task.get('passage') or ''
      segments=re.split(r'(?=\b(?:Interviewer|Host|Student|Teacher|A|B)\s*:)',passage)
      turns=[]
      for seg in segments:
        m=re.match(r'\s*(Interviewer|Host|Student|Teacher|A|B)\s*:\s*(.+)',seg,flags=re.S)
        if m:turns.append((m.group(2).strip(),0 if m.group(1) in ('Interviewer','Host','Teacher','A') else 1))
      if not turns:turns=[(passage,0)]
      for repeat in range(2):
        for text,voice in turns:
          await speak(text,voice);pause(.6)
        pause(3)
    concat=temp/'list.txt'
    concat.write_text(''.join("file '"+str(f.resolve()).replace("'","'\\''")+"'\n" for f in parts))
    out=OUT/f'{task["id"]}.mp3'
    ff('-f','concat','-safe','0','-i',concat,'-ac','1','-ar','44100','-c:a','libmp3lame','-b:a','96k',out)
    assert out.stat().st_size>15000 and MP3(out).info.length>35,out
    print('VALID',out.relative_to(ROOT),round(MP3(out).info.length),'sec',flush=True)
async def main():
  for task in TASKS:
    if task.get('skill')=='listening':await make(task)
if __name__=='__main__':asyncio.run(main())
