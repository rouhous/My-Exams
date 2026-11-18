#!/usr/bin/env python3
"""Generate original Grade 9 Listening B/C/G as downloadable local MP3.
Uses Edge Neural TTS where available, then Google TTS as a fallback.
Both attempts are checked for actual MP3 audio; failures stop the release.
"""
import asyncio, json, pathlib, re, subprocess, tempfile, hashlib, os
from listening_voice_roles import VOICE_NAMES, parse_dialogue, voice_for_narration
from mutagen.mp3 import MP3
import edge_tts

ROOT=pathlib.Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'grade9/data.json').read_text(encoding='utf-8'))
OUT=ROOT/'grade9/audio-natural'
OUT.mkdir(parents=True,exist_ok=True)
VOICES=VOICE_NAMES
SAMPLE_RATE='44100'

def ffmpeg(*args):
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)

def silence(path,seconds):
    ffmpeg('-f','lavfi','-i',f'anullsrc=channel_layout=mono:sample_rate={SAMPLE_RATE}',
           '-t',str(seconds),'-c:a','libmp3lame','-b:a','96k',path)

async def speech(text,path,voice):
    text=re.sub(r'\s+',' ',text).strip()
    if not text:raise ValueError('Empty TTS input')
    # Do not silently fall back to a voice with unknown gender or accent.
    await edge_tts.Communicate(text,voice,rate='-8%').save(str(path))
    if path.stat().st_size<1500 or MP3(path).info.length<0.4:
        raise ValueError('Edge voice unavailable; do not publish a mismatched narrator')
    print('edge:',voice,text[:40],flush=True)

async def build(model,task,tmp):
    clips=[]
    spoken={};used_voices=set();speaker_cast={};playback_sequence=[]
    async def say(text,voice=0):
        key=(text,voice)
        if key not in spoken:
            p=tmp/f'speech-{len(spoken):03d}.mp3'
            await speech(text,p,VOICES[voice])
            spoken[key]=p
        used_voices.add(VOICES[voice]);clips.append(spoken[key])
    def pause(seconds):
        p=tmp/f'{len(clips):03d}.mp3';silence(p,seconds);clips.append(p)
    if task['group']==1:
        await say('You are going to hear five short texts. For each text, choose the correct picture, A, B or C. You will hear the texts twice.')
        pause(3)
        if len(task['items'])!=5:
            raise ValueError('Listening 1 must contain five short texts: '+task['id'])
        labels=('one','two','three','four','five')
        for repetition in range(2):
            if repetition:
                playback_sequence.append('now-listen-again')
                await say('Now listen again.')
                pause(2)
            for i,item in enumerate(task['items']):
                playback_sequence.append('text-'+labels[i])
                spoken_text=re.sub(r'^Text (?:one|two|three|four|five|[1-5])[. :]+','',item['script'],flags=re.I)
                voice=voice_for_narration(spoken_text,item.get('speakerGender'),fallback_voice=i%2)
                await say(f'Text {labels[i]}. '+spoken_text,voice)
                pause(3)
    else:
        await say('You are going to hear an interview. Listen carefully and choose the correct answer, A, B or C. You will hear the interview twice.')
        pause(3)
        parts_with_labels=parse_dialogue(task['transcript'],task.get('speakerGenders'))
        parts=[(text,voice) for text,voice,_ in parts_with_labels]
        speaker_cast={name:VOICES[voice] for text,voice,name in parts_with_labels}
        if len(parts)<6:raise ValueError('Listening interview not split correctly: '+task['id'])
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
    return {'usedVoices':sorted(used_voices),'speakerCast':speaker_cast,'playbackSequence':playback_sequence}

async def main():
    prior_manifest_path=OUT/'manifest.json'
    prior=json.loads(prior_manifest_path.read_text(encoding='utf-8')) if prior_manifest_path.exists() else {}
    manifest={}
    selected_models=set(filter(None,(x.strip().upper() for x in os.environ.get('ONLY_MODELS','B,C,G').split(','))))
    selected_tasks=set(filter(None,(x.strip() for x in os.environ.get('ONLY_LISTENING_IDS','').split(','))))
    for m in DATA['models']:
        if m['model'] not in selected_models:continue
        with tempfile.TemporaryDirectory() as d:
            for t in m['tasks']:
                if t.get('skill')!='listening' or (selected_tasks and t['id'] not in selected_tasks):continue
                source={'transcript':t.get('transcript'),'items':t.get('items'),'questions':t.get('questions'),'speakerGenders':t.get('speakerGenders')}
                fingerprint=hashlib.sha256(json.dumps(source,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
                mp3=f"g9-{m['model'].lower()}-listening-{t['group']}.mp3"
                target=OUT/mp3
                old=prior.get(t['id'],{})
                if (old.get('sourceHash')==fingerprint and old.get('mp3')==mp3
                        and target.is_file() and target.stat().st_size>15000
                        and MP3(target).info.length>40 and old.get('voiceRoutingVersion')=='identity-v2'):
                    print('REUSE exact source-verified MP3:',t['id'])
                    voice_meta={'usedVoices':old['usedVoices'],'speakerCast':old.get('speakerCast',{})}
                else:
                    print('REBUILD stale or absent MP3:',t['id'])
                    with tempfile.TemporaryDirectory(dir=d) as taskdir:
                        voice_meta=await build(m['model'],t,pathlib.Path(taskdir))
                manifest[t['id']]={'sourceHash':fingerprint,'mp3':mp3,
                    'sourceModel':m['model'],'seconds':round(MP3(target).info.length,2),
                    'bytes':target.stat().st_size,'playedTwice':True,'voiceRoutingVersion':'identity-v2',**voice_meta}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    expected=sum(1 for m in DATA['models'] if m['model'] in selected_models for t in m['tasks'] if t.get('skill')=='listening' and (not selected_tasks or t['id'] in selected_tasks))
    assert len(manifest)==expected,(len(manifest),expected)
if __name__=='__main__':asyncio.run(main())
