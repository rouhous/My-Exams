#!/usr/bin/env python3
"""Generate Grade 8 Model A exam listening, two natural voices and offline-ready MP3."""
import asyncio,json,pathlib,re,subprocess,tempfile
import edge_tts
from mutagen.mp3 import MP3

ROOT=pathlib.Path(__file__).resolve().parents[1]
tasks=json.loads((ROOT/'tasks_5_to_9_corrected.json').read_text())
A=tasks['8:A:listening1']['data']
B=tasks['8:A:listening2']['data']
DEST=ROOT/'grades7-8/assets/audio'
DEST.mkdir(parents=True,exist_ok=True)
VOICE_A='en-GB-SoniaNeural'
VOICE_B='en-GB-RyanNeural'

def ffmpeg(*args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*map(str,args)],check=True)
def validate(f):
    d=MP3(f).info.length
    if d<1 or f.stat().st_size<1500:raise ValueError(f'Audio invalid {f}: {d}')
    return d
async def speech(t,path,voice=VOICE_A):
    await edge_tts.Communicate(t,voice,rate='-7%').save(str(path))
    validate(path)
def silent(path,seconds):
    ffmpeg('-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=44100','-t',seconds,'-c:a','libmp3lame','-b:a','96k',path)
def merge(chunks,target,temp):
    entries=temp/'list.txt'
    entries.write_text(''.join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in chunks))
    ffmpeg('-f','concat','-safe','0','-i',entries,'-ar','44100','-ac','1','-c:a','libmp3lame','-b:a','96k',target)
    duration=validate(target)
    if duration<100:raise ValueError(f'Suspiciously short final audio {duration}')
    print(str(target.relative_to(ROOT)),round(duration,1),'sec',target.stat().st_size,'bytes',flush=True)
async def listening1(temp):
    intro=temp/'intro.mp3'
    await speech('You are going to hear five short texts. For each text, choose the correct picture, A, B or C. You will hear the texts twice.',intro)
    clips=[]
    for i,x in enumerate(A['items']):
        p=temp/f'text{i+1}.mp3'
        await speech(f'Text {i+1}. '+x['script'],p,VOICE_B if i%2 else VOICE_A)
        clips.append(p)
    three=temp/'pause3.mp3';silent(three,3)
    five=temp/'pause5.mp3';silent(five,5)
    # Read instruction once, then first pass five texts with 3-second pauses; pause 5 sec; repeat.
    sequence=[intro,three]
    for repetition in range(2):
        for i,clip in enumerate(clips):
            sequence.append(clip)
            if i<4:sequence.append(three)
        if repetition==0:sequence.append(five)
    merge(sequence,DEST/'natural-g8-a-listening1.mp3',temp)
async def listening2(temp):
    intro=temp/'intro.mp3'
    await speech('You are going to hear a dialogue. Listen carefully and decide if each statement is true or false. You will hear the dialogue twice.',intro)
    original=B['script']
    pieces=re.split(r'(?=(?:Interviewer|Hind):)',original)
    turns=[]
    for part in pieces:
        match=re.match(r'\s*(Interviewer|Hind):\s*(.+)',part,flags=re.S)
        if match:turns.append(match.groups())
    if len(turns)<6:raise ValueError('Cannot separate dialogue turns')
    clips=[]
    for i,(speaker,line) in enumerate(turns):
        p=temp/f'turn{i:02d}.mp3';await speech(line.strip(),p,VOICE_B if speaker=='Interviewer' else VOICE_A)
        clips.append(p)
    pause=temp/'pause.mp3';silent(pause,0.65)
    gap=temp/'gap.mp3';silent(gap,5)
    sequence=[intro,gap]
    for repetition in range(2):
        for i,clip in enumerate(clips):
            sequence.append(clip)
            if i<len(clips)-1:sequence.append(pause)
        if repetition==0:sequence.append(gap)
    merge(sequence,DEST/'natural-g8-a-listening2.mp3',temp)
async def main():
    with tempfile.TemporaryDirectory() as d:
        tmp=pathlib.Path(d)
        l1=tmp/'l1';l1.mkdir()
        l2=tmp/'l2';l2.mkdir()
        await listening1(l1);await listening2(l2)
if __name__=='__main__':asyncio.run(main())
