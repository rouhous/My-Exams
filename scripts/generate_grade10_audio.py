#!/usr/bin/env python3
"""Grade 10 unit-paper natural audio pilot; English TTS, twice with pauses."""
import asyncio,hashlib,json,pathlib,re,shutil,subprocess,tempfile
import edge_tts
from mutagen.mp3 import MP3
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'grade10/data.json').read_text())
OUT=ROOT/'grade10/audio'
OUT.mkdir(exist_ok=True)
VOICES=('en-GB-SoniaNeural','en-GB-RyanNeural')
def ff(*args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
async def one(model):
    passage=model['listening']['passage']
    with tempfile.TemporaryDirectory() as d:
        tmp=pathlib.Path(d);cache={};seq=[]
        async def speak(text,voice):
            key=(text,voice)
            if key not in cache:
                p=tmp/f'voice{len(cache):03d}.mp3'
                await edge_tts.Communicate(text,VOICES[voice],rate='-9%').save(str(p))
                if p.stat().st_size<1200:raise ValueError('Invalid natural audio')
                cache[key]=p
            seq.append(cache[key])
        def pause(sec):
            p=tmp/f'pause{len(seq):03d}.mp3'
            ff('-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=44100','-t',sec,'-c:a','libmp3lame','-b:a','96k',p)
            seq.append(p)
        await speak('You will hear a recording related to '+model['unitTitle']+'. Listen carefully and answer the questions. You will hear the recording twice.',0)
        pause(3)
        chunks=re.split(r'(?=\b(?:Teacher|Maha|Presenter|Student|Engineer|Guide|Visitor|Interviewer|Speaker)\s*:)',passage)
        turns=[]
        for p in chunks:
            m=re.match(r'\s*([A-Za-z]+)\s*:\s*(.+)',p,flags=re.S)
            if m:turns.append((m.group(2).strip(),0 if m.group(1) in ('Teacher','Presenter','Engineer','Guide','Interviewer') else 1))
        if len(turns)<2:turns=[(passage,0)]
        for repeat in range(2):
            for text,voice in turns:
                await speak(text,voice)
                pause(.45)
            pause(3)
        listing=tmp/'list.txt'
        listing.write_text(''.join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in seq))
        dest=OUT/f'g10-{model["id"].lower()}-listening.mp3'
        ff('-f','concat','-safe','0','-i',listing,'-ac','1','-ar','44100','-c:a','libmp3lame','-b:a','96k',dest)
        if dest.stat().st_size<20000 or MP3(dest).info.length<60:raise ValueError(dest)
        return dest
async def main():
    unique={}
    old_manifest=json.loads((OUT/'manifest.json').read_text()) if (OUT/'manifest.json').exists() else {}
    manifest={}
    for model in DATA['models']:
        passage=model['listening']['passage']
        h=hashlib.sha256(passage.encode()).hexdigest()
        if h not in unique:
            previous=old_manifest.get(model['id'],{})
            existing=OUT/f'g10-{model["id"].lower()}-listening.mp3'
            if previous.get('passage_sha256')==h and existing.exists() and existing.stat().st_size>20000 and MP3(existing).info.length>60:
                unique[h]=existing
                print('REUSING verified existing natural source',existing.name,flush=True)
            else:
                unique[h]=await one(model)
        out=OUT/f'g10-{model["id"].lower()}-listening.mp3'
        if unique[h]!=out:shutil.copyfile(unique[h],out)
        manifest[model['id']]={'mp3':out.name,'sourceModel':unique[h].name[4].upper(),'passage_sha256':h,'seconds':round(MP3(out).info.length,1),'size':out.stat().st_size}
        print('OK',model['id'],out.name,manifest[model['id']]['seconds'],'seconds',flush=True)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':asyncio.run(main())
