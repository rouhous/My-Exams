#!/usr/bin/env python3
"""Record Grade 11 Core separate official-shaped nine-section paper A listening 1+2.
Source is grade11/core/semester-a.html; scripts are teacher-review material, not certified.
"""
import asyncio,hashlib,json,pathlib,re,subprocess,tempfile
from bs4 import BeautifulSoup
import edge_tts
from mutagen.mp3 import MP3
ROOT=pathlib.Path(__file__).resolve().parents[1]
HTML=ROOT/'grade11/core/semester-a.html'
OUT=ROOT/'grade11/core/semester-a/audio'
OUT.mkdir(parents=True,exist_ok=True)
SPEAKERS=('en-GB-SoniaNeural','en-GB-RyanNeural')
def ff(*args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
async def write_audio(script,part):
  with tempfile.TemporaryDirectory() as d:
    tmp=pathlib.Path(d);cache={};files=[]
    async def speak(text,voice):
      text=re.sub(r'\s+',' ',text).strip()
      if not text:return
      key=(text,voice)
      if key not in cache:
        p=tmp/f's{len(cache)}.mp3'
        for i in range(4):
          try:
            await edge_tts.Communicate(text,SPEAKERS[voice],rate='-7%').save(str(p))
            if p.stat().st_size<1500:raise ValueError("Invalid neural file")
            break
          except Exception:
            if i==3:raise
            await asyncio.sleep(2**i)
        cache[key]=p
      files.append(cache[key])
    def pause(sec):
      p=tmp/f'p{len(files)}.mp3';ff('-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=44100','-t',sec,'-c:a','libmp3lame','-b:a','96k',p);files.append(p)
    await speak('You are going to hear a recording. Listen carefully, then answer the questions. You will hear it twice.',0);pause(3)
    if part=='lst1':
      parsed=[]
      for line in script.splitlines():
        m=re.match(r"^(Maha|Nasser):\s*(.*)$",line.strip())
        if not m:raise ValueError('Unrecognized dialogue turn: '+line)
        parsed.append((m.group(2),0 if m.group(1)=='Maha' else 1))
      assert 25<=len(parsed)<=30
    else:
      parsed=[(x.strip().replace('\n',' '),0) for x in script.split('Part Two')]
      if len(parsed)!=2:raise ValueError('Need two parts in listening 2')
      parsed=[('Part One. '+parsed[0].replace('Part One','',1),0),('Part Two. '+parsed[1],0)]
    for repeat_index in range(2):
      for text,voice in parsed:await speak(text,voice);pause(.7)
      pause(5 if repeat_index==0 else 3)
    concat=tmp/'list.txt';concat.write_text(''.join("file '"+str(x.resolve()).replace("'","'\\''")+"'\n" for x in files))
    target=OUT/(part+'.mp3')
    ff('-f','concat','-safe','0','-i',concat,'-ac','1','-ar','44100','-c:a','libmp3lame','-b:a','96k',target)
  secs=MP3(target).info.length
  assert target.stat().st_size>20000 and secs>120
  return target,round(secs,2)
async def main():
  soup=BeautifulSoup(HTML.read_text(),'html.parser')
  sections=[s for s in soup.select('section') if s.h2 and s.h2.get_text(strip=True).startswith('Listening')]
  assert len(sections)==2,len(sections)
  manifest={}
  for i,sec in enumerate(sections,1):
    script=sec.select_one('details.teacher p').get_text('\n').strip()
    part='lst'+str(i)
    count=len(script.split())
    if i==1:assert 300<=count<=350
    if i==2:assert 350<=count<=400
    target,secs=await write_audio(script,part)
    manifest[part]={'mp3':target.name,'scriptSha256':hashlib.sha256(script.encode()).hexdigest(),'words':count,'seconds':secs,'bytes':target.stat().st_size,'playedTwice':True,'contentApproved':False}
    print('RECORDED',part,count,secs,flush=True)
  (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':asyncio.run(main())
