#!/usr/bin/env python3
"""Generate Grade 10 full twice-read interviews using identity-safe British voices.

Unknown generic roles use an explicit editorial audition cast, not pronouns
about third parties. Preview replacements can override speakers via source JSON.
"""
import asyncio,hashlib,json,os,pathlib,shutil,subprocess,tempfile
import edge_tts
from mutagen.mp3 import MP3
from listening_voice_roles import VOICE_NAMES,parse_dialogue
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'grade10/data.json').read_text(encoding='utf-8'))
OUT=ROOT/'grade10/audio'
OUT.mkdir(parents=True,exist_ok=True)
VOICES=VOICE_NAMES
# Audition casting for unidentified generic roles (must be teacher-reviewed).
# 0 Sonia (female host); 1 Ryan (male participant); 2 Libby (female guest).
ROLE_AUDITION_CAST={
 'A':{'Teacher':0},'B':{'Presenter':0},
 'C':{'Engineer':0,'Student':1},'D':{'Guide':0,'Student':1},
 'E':{'Teacher':0},'F':{'Guide':0,'Student':1},
}
def ff(*args):
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
def actor_cast(model):
 task=model['listening']
 script=task['passage']
 role_cast=ROLE_AUDITION_CAST.get(model['id'],{})
 # Named speakers must be in the reviewed registry or have explicit source metadata.
 genders={name:'male' if index==1 else 'female' for name,index in role_cast.items()}
 genders.update(task.get('speakerGenders') or {})
 raw=parse_dialogue(script,genders)
 if len(raw)<4:raise ValueError('Invalid Grade 10 interview: '+model['id'])
 turns=[]
 for text,voice,name in raw:
  if name in role_cast and name not in (task.get('speakerGenders') or {}):
   voice=role_cast[name]
  turns.append((text,voice,name))
 return turns

async def one(model):
 turns=actor_cast(model)
 used=set()
 with tempfile.TemporaryDirectory() as d:
  tmp=pathlib.Path(d);cache={};seq=[]
  async def speak(text,voice=0):
   text=' '.join(text.split()).strip()
   if not text:return
   key=(text,voice)
   if key not in cache:
    out=tmp/f'voice{len(cache):03d}.mp3'
    await edge_tts.Communicate(text,VOICES[voice],rate='-9%').save(str(out))
    if out.stat().st_size<1200 or MP3(out).info.length<0.4:
     raise ValueError('Natural voice unavailable; do not publish unverified fallback')
    cache[key]=out
   used.add(VOICES[voice]);seq.append(cache[key])
  def pause(sec):
   f=tmp/f'pause{len(seq):03d}.mp3'
   ff('-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=44100','-t',sec,'-c:a','libmp3lame','-b:a','96k',f)
   seq.append(f)
  await speak('You will hear a recording related to '+model['unitTitle']+'. Listen carefully and answer the questions. You will hear the recording twice.')
  pause(3)
  for repeat in range(2):
   if repeat:
    await speak('Now listen again.')
    pause(2)
   for text,voice,label in turns:
    await speak(text,voice)
    pause(.45)
   pause(3)
  listing=tmp/'list.txt'
  listing.write_text(''.join("file '"+str(f.resolve()).replace("'","'\\''")+"'"+'\n' for f in seq))
  dest=OUT/f'g10-{model["id"].lower()}-listening.mp3'
  ff('-f','concat','-safe','0','-i',listing,'-ac','1','-ar','44100','-c:a','libmp3lame','-b:a','96k',dest)
  if dest.stat().st_size<20000 or MP3(dest).info.length<60:
   raise ValueError('Invalid generated MP3: '+str(dest))
  return dest,{'usedVoices':sorted(used),
               'speakerCast':{name:VOICES[voice] for _,voice,name in turns},
               'voiceRoutingVersion':'identity-v2','playedTwice':True}
async def main():
 requested=set(filter(None,(s.strip().upper() for s in os.environ.get('ONLY_MODELS','').split(','))))
 seen={}
 prior_path=OUT/'manifest.json'
 prior=json.loads(prior_path.read_text(encoding='utf-8')) if prior_path.exists() else {}
 manifest={}
 for model in DATA['models']:
  if requested and model['id'] not in requested:continue
  turns=actor_cast(model)
  src={'passage':model['listening']['passage'],
       'speakerGenders':model['listening'].get('speakerGenders'),
       'speakerCast':{name:VOICES[voice] for _,voice,name in turns},
       'voiceRoutingVersion':'identity-v2'}
  h=hashlib.sha256(json.dumps(src,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
  dest=OUT/f'g10-{model["id"].lower()}-listening.mp3'
  if h in seen:
   master,meta=seen[h]
   if master!=dest:shutil.copyfile(master,dest)
  else:
   old=prior.get(model['id'],{})
   if old.get('source_sha256')==h and old.get('speakerCast')==src['speakerCast'] and dest.exists() and dest.stat().st_size>20000 and MP3(dest).info.length>60:
    meta={key:old[key] for key in ('speakerCast','usedVoices','playedTwice','voiceRoutingVersion')}
    print('REUSE source & voice audited',dest.name,flush=True)
   else:
    dest,meta=await one(model)
   seen[h]=(dest,meta)
  manifest[model['id']]={'mp3':dest.name,'sourceModel':seen[h][0].name[4].upper(),
     'source_sha256':h,'seconds':round(MP3(dest).info.length,1),
     'size':dest.stat().st_size,**meta}
  print('VALID',model['id'],dest.name,round(MP3(dest).info.length),'sec',flush=True)
 (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 if requested and set(manifest)!=requested:raise ValueError('Requested models missing from manifest')
if __name__=='__main__':asyncio.run(main())
