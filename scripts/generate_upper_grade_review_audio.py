#!/usr/bin/env python3
"""Natural MP3 for provisional, UNAPPROVED upper-grade source bank."""
import asyncio,hashlib,json,pathlib,re,shutil,subprocess,sys,tempfile
import edge_tts
from mutagen.mp3 import MP3
R=pathlib.Path(__file__).resolve().parents[1];TRACK=sys.argv[1]
assert TRACK in ('11-elective','12-core','12-elective')
data=json.loads((R/'higher_grades_corrected.json').read_text())[TRACK]
out=R/'upper-audio'/TRACK;out.mkdir(parents=True,exist_ok=True)
voices=('en-GB-SoniaNeural','en-GB-RyanNeural')
def ff(*args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
async def build(src,key,target):
  passage=(src.get('script') or src['passage']).strip()
  if key=='lst1':
    matches=[re.match(r"^\s*([A-Za-z .'-]{2,40}):\s*(.+)$",line.strip()) for line in passage.splitlines()]
    pairs=[(m.group(1).strip(),m.group(2).strip()) for m in matches if m]
    names=list(dict.fromkeys(x[0] for x in pairs))
    if len(pairs)>2 and 1<len(names)<=3:
      turns=[(t,names.index(n)%2) for n,t in pairs];voice_mode='two_voices'
    else:turns=[(passage,0)];voice_mode='one_reader_unparsed_dialogue'
  else:
    turns=[(x.strip().replace('\n',' '),0) for x in re.split(r'\n\s*\n',passage) if x.strip()]
    voice_mode='one_voice'
  with tempfile.TemporaryDirectory() as d:
    p=pathlib.Path(d);seen={};items=[]
    async def say(t,v):
      t=re.sub(r'\s+',' ',t).strip()
      if not t:return
      k=(t,v)
      if k not in seen:
        f=p/f'a{len(seen)}.mp3'
        for i in range(4):
          try:
            await edge_tts.Communicate(t,voices[v],rate='-8%').save(str(f))
            if f.stat().st_size<1500:raise ValueError('bad speech response')
            break
          except Exception:
            if i==3:raise
            await asyncio.sleep(2**i)
        seen[k]=f
      items.append(seen[k])
    def pause(sec):
      f=p/f's{len(items)}.mp3';ff('-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=44100','-t',sec,'-c:a','libmp3lame','-b:a','96k',f);items.append(f)
    await say('Listen carefully. This recording will be played twice.',0);pause(3)
    for round in range(2):
      for t,v in turns:await say(t,v);pause(.6)
      pause(4 if round==0 else 2)
    lst=p/'concat.txt';lst.write_text(''.join("file '"+str(x.resolve()).replace("'","'\\''")+"'\n" for x in items))
    ff('-f','concat','-safe','0','-i',lst,'-ac','1','-ar','44100','-c:a','libmp3lame','-b:a','96k',target)
  duration=MP3(target).info.length
  assert duration>120 and target.stat().st_size>20000
  return round(duration,2),voice_mode
async def main():
  prior=json.loads((out/'manifest.json').read_text()) if (out/'manifest.json').is_file() else {}
  manifest={};seen={}
  for model in data:
    for p in model['parts']:
      if p['key'] not in ('lst1','lst2'):continue
      src=(p.get('script') or p['passage']).strip()
      h=hashlib.sha256(src.encode()).hexdigest()
      key=model['id']+'-'+p['key']
      target=out/(model['id'].lower()+'-'+p['key']+'.mp3')
      if h in seen:
        e=seen[h];shutil.copyfile(out/e['mp3'],target);seconds,mode=e['seconds'],e['voiceMode']
      elif key in prior and prior[key].get('passageSha256')==h and target.is_file() and target.stat().st_size>20000:
        seconds,mode=round(MP3(target).info.length,2),prior[key]['voiceMode']
      else:seconds,mode=await build(p,p['key'],target)
      e={'mp3':target.name,'passageSha256':h,'seconds':seconds,'voiceMode':mode,'bytes':target.stat().st_size,'readTwice':True,'contentApproval':'teacher_review_required'}
      manifest[key]=e;seen[h]=e
      print('RECORDED',TRACK,key,seconds,mode,flush=True)
  assert len(manifest)==12
  (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':asyncio.run(main())
