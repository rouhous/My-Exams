#!/usr/bin/env python3
"""Generate original Grade 9 Listening B/C/G as downloadable local MP3.
Uses Edge Neural TTS where available, then Google TTS as a fallback.
Both attempts are checked for actual MP3 audio; failures stop the release.
"""
import asyncio, json, pathlib, re, subprocess, tempfile, hashlib
from gtts import gTTS
from mutagen.mp3 import MP3
import edge_tts

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'grade9/data.json').read_text(encoding='utf-8'))
OUT=ROOT/'grade9/audio-natural'
OUT.mkdir(parents=True,exist_ok=True)
VOICES=['en-GB-SoniaNeural','en-GB-RyanNeural']
SAMPLE_RATE='44100'

def ffmpeg(*args):
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)

def silence(path,seconds):
    ffmpeg('-f','lavfi','-i',f'anullsrc=channel_layout=mono:sample_rate={SAMPLE_RATE}',
           '-t',str(seconds),'-c:a','libmp3lame','-b:a','96k',path)

async def speech(text,path,voice):
    text=re.sub(r'\s+',' ',text).strip()
    if not text:raise ValueError('Empty TTS input')
    try:
        await edge_tts.Communicate(text,voice,rate='-8%').save(str(path))
        if path.stat().st_size<1500 or MP3(path).info.length<0.4:raise ValueError('Edge audio too small')
        print('edge:',voice,text[:40])
        return
    except Exception as e:
        print('Edge TTS failed; trying gTTS:',str(e)[:130])
    gTTS(text=text,lang='en',tld='co.uk',slow=False).save(str(path))
    if path.stat().st_size<1500 or MP3(path).info.length<0.4:raise ValueError('No valid speech from TTS')
    print('gTTS:',text[:40])

def split_interview(transcript):
    text=transcript.replace('\r',' ').replace('\n',' ')
    parts=re.split(r'(?=\b(?:Interviewer|Salim|Alya|Rashid)\s*:)',text)
    out=[]
    for part in parts:
        m=re.match(r'\s*(Interviewer|Salim|Alya|Rashid)\s*:\s*(.+)',part,flags=re.S)
        if m:out.append((m.group(2).strip(),0 if m.group(1)=='Interviewer' else 1))
    if len(out)<6:raise ValueError('Interview not split correctly')
    return out

async def build(model,task,tmp):
    clips=[]
    spoken={}
    async def say(text,voice=0):
        key=(text,voice)
        if key not in spoken:
            p=tmp/f'speech-{len(spoken):03d}.mp3'
            await speech(text,p,VOICES[voice])
            spoken[key]=p
        clips.append(spoken[key])
    def pause(seconds):
        p=tmp/f'{len(clips):03d}.mp3';silence(p,seconds);clips.append(p)
    if task['group']==1:
        await say('You are going to hear five short texts. For each text, choose the correct picture, A, B or C. You will hear the texts twice.')
        pause(3)
        for i,item in enumerate(task['items']):
            for repetition in range(2):
                await say(f'Text {i+1}. '+re.sub(r'^Text (?:one|two|three|four|five|[1-5])[. :]+','',item['script'],flags=re.I),i%2)
                pause(3)
    else:
        await say('You are going to hear an interview. Listen carefully and choose the correct answer, A, B or C. You will hear the interview twice.')
        pause(3)
        parts=split_interview(task['transcript'])
        for repetition in range(2):
            for text,voice in parts:
                await say(text,voice)
                pause(0.65)
            pause(4)
    listfile=tmp/'concat.txt'
    listfile.write_text(''.join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in clips))
    output=OUT/f'g9-{model.lower()}-listening-{task["group"]}.mp3'
    ffmpeg('-f','concat','-safe','0','-i',listfile,'-ac','1','-ar',SAMPLE_RATE,
           '-c:a','libmp3lame','-b:a','96k',output)
    duration=MP3(output).info.length
    if duration<40 or output.stat().st_size<15000:raise ValueError(f'Audio invalid: {output}, {duration}s')
    print('CREATED',output.relative_to(ROOT),round(duration,1),'seconds',output.stat().st_size,'bytes')

async def main():
    manifest={}
    for m in DATA['models']:
        if m['model'] not in {'B','C','G'}:continue
        with tempfile.TemporaryDirectory() as d:
            for t in m['tasks']:
                if t.get('skill')=='listening':
                    with tempfile.TemporaryDirectory(dir=d) as taskdir:
                        await build(m['model'],t,pathlib.Path(taskdir))
                        source={'transcript':t.get('transcript'),'items':t.get('items'),'questions':t.get('questions')}
                        fingerprint=hashlib.sha256(json.dumps(source,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
                        mp3=f"g9-{m['model'].lower()}-listening-{t['group']}.mp3"
                        manifest[t['id']]={'sourceHash':fingerprint,'mp3':mp3,'sourceModel':m['model'],'seconds':round(MP3(OUT/mp3).info.length,2),'bytes':(OUT/mp3).stat().st_size,'playedTwice':True}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    assert len(manifest)==6
if __name__=='__main__':asyncio.run(main())
