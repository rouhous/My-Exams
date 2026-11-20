#!/usr/bin/env python3
"""Grade 5 and 6: natural MP3 with Ministry-style instructions and pauses."""
import asyncio,json,pathlib,re,subprocess,tempfile,hashlib
import edge_tts
from mutagen.mp3 import MP3
from listening_voice_roles import VOICE_NAMES, parse_dialogue, voice_for_narration
ROOT=pathlib.Path(__file__).resolve().parents[1]
TASKS=json.loads((ROOT/'grades5-6/activities.json').read_text(encoding='utf-8'))['activities']
OUT=ROOT/'grades5-6/audio-natural'
OUT.mkdir(parents=True,exist_ok=True)
VOICES=VOICE_NAMES
MANIFEST={}
def ff(*args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
async def make(task):
  with tempfile.TemporaryDirectory() as d:
    temp=pathlib.Path(d);cache={};parts=[];usedVoices=set();speaker_cast={}
    async def speak(text,voice=0):
      text=re.sub(r'\s+',' ',text).strip()
      if not text:return
      key=(text,voice)
      if key not in cache:
        f=temp/f'voice{len(cache):03d}.mp3'
        await edge_tts.Communicate(text,VOICES[voice],rate='-10%').save(str(f))
        assert f.stat().st_size>1500,f
        cache[key]=f
      usedVoices.add(VOICES[voice]);parts.append(cache[key])
    def pause(sec):
      f=temp/f'pause{len(parts):03d}.mp3'
      ff('-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=44100','-t',sec,'-c:a','libmp3lame','-b:a','96k',f)
      parts.append(f)
    if task['part']==1:
      await speak('You are going to hear five short dialogues. For each dialogue, choose the correct picture. You will hear the dialogues twice.')
      pause(3)
      # Play all five in order, then repeat the complete sequence.
      # Do NOT repeat each short text immediately after it is read.
      prepared=[]
      for i,dialogue in enumerate(task['passages']):
        parsed=[(words,voice) for words,voice,_ in parse_dialogue(dialogue,task.get('speakerGenders'))]
        if not parsed:
          hints=task.get('textSpeakerGenders') or []
          explicit=hints[i] if i<len(hints) else None
          parsed=[(dialogue,voice_for_narration(dialogue,explicit,fallback_voice=i%2))]
        prepared.append(parsed)
      labels=('one','two','three','four','five')
      for repeat in range(2):
        if repeat:
          await speak('Now listen again.')
          pause(2)
        for i,parsed in enumerate(prepared):
          await speak(f'Text {labels[i]}.')
          for text,voice in parsed:
            await speak(text,voice);pause(.5)
          pause(3)
    else:
      await speak('You are going to hear a dialogue or interview. Listen carefully and choose the correct answers. You will hear it twice.')
      pause(3)
      passage=task.get('passage') or ''
      labeled_turns=parse_dialogue(passage,task.get('speakerGenders'))
      turns=[(words,voice) for words,voice,_ in labeled_turns]
      speaker_cast={name:VOICES[voice] for _,voice,name in labeled_turns}
      if len(turns)<5:raise ValueError('Listening interview needs at least five explicit turns: '+task['id'])
      for repeat in range(2):
        for text,voice in turns:
          await speak(text,voice);pause(.6)
        pause(3)
    concat=temp/'list.txt'
    concat.write_text(''.join("file '"+str(f.resolve()).replace("'","'\\''")+"'\n" for f in parts))
    out=OUT/f'{task["id"]}.mp3'
    ff('-f','concat','-safe','0','-i',concat,'-ac','1','-ar','44100','-c:a','libmp3lame','-b:a','96k',out)
    assert out.stat().st_size>15000 and MP3(out).info.length>35,out
    MANIFEST[task['id']]={'sha256_of_script':hashlib.sha256(json.dumps({'passages':task.get('passages'),'passage':task.get('passage'),'questions':task['questions'],'pictures':task.get('pictureOptions')},sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'mp3':out.name,'size':out.stat().st_size,'seconds':round(MP3(out).info.length,2),'voices':list(VOICES),'usedVoices':sorted(usedVoices),'speakerCast':speaker_cast,'voiceRoutingVersion':'identity-v2'}
    print('VALID',out.relative_to(ROOT),round(MP3(out).info.length),'sec',flush=True)
async def main():
  selected=set(filter(None,(x.strip() for x in __import__('os').environ.get('ONLY_LISTENING_IDS','').split(','))))
  for task in TASKS:
    if task.get('skill')=='listening' and (not selected or task['id'] in selected):await make(task)
  (OUT/'script_audio_manifest.json').write_text(json.dumps(MANIFEST,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':asyncio.run(main())
