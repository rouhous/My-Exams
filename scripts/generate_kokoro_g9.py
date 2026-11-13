#!/usr/bin/env python3
"""Produce English Grade 9 C and D/G listening MP3 via Apache-2.0 Kokoro-82M.
Each file is a single named listening segment. The HTML player adds timed
3-second gaps and repeats the sequence exactly twice.
"""
import json, pathlib, subprocess, tempfile, sys
import numpy as np
import soundfile as sf
from kokoro import KPipeline
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/'grade9/teacher/natural_scripts_BCD_v2.json'
segments=json.loads(SOURCE.read_text(encoding='utf-8'))['segments']
tasks=[x for x in segments if x['model'] in ('C','D')]
pipeline=KPipeline(lang_code='b') # English British pronunciation, clear exam narration
voice_map={
 'C':{'narrator':'bf_emma','interviewer':'bm_george','guest':'bf_isabella'},
 'D':{'narrator':'bf_emma','interviewer':'bf_emma','guest':'bm_george'}
}
done=0
for s in tasks:
    model=s['model'].lower()
    out=ROOT/'audio-natural/g9'/model/s['section']/(s['segment']+'.mp3')
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists() and out.stat().st_size>1024:
        done+=1;continue
    voice=voice_map[s['model']][s['role']]
    chunks=[]
    for _,_,audio in pipeline(s['text'],voice=voice,speed=0.96,split_pattern=r'\n+'):
        audio=np.asarray(audio,dtype=np.float32).reshape(-1)
        if audio.size:chunks.append(audio)
    if not chunks:raise RuntimeError('No speech generated for '+str(out))
    # Keep long turns audible and smooth; HTML supplies between-turn pauses.
    audio=np.concatenate(chunks)
    with tempfile.TemporaryDirectory() as temp:
        wav=pathlib.Path(temp)/'voice.wav'
        sf.write(wav,audio,24000)
        subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y',
                        '-i',str(wav),'-ar','24000','-codec:a','libmp3lame',
                        '-b:a','96k',str(out)],check=True)
    assert out.stat().st_size>1024,(s['segment'],out.stat().st_size)
    print('OK',s['model'],s['section'],s['segment'],round(len(audio)/24000,1),out.stat().st_size,flush=True)
    done+=1
print('GENERATED OR VERIFIED:',done,'OF',len(tasks))
if done!=len(tasks):sys.exit(1)
