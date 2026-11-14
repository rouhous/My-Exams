#!/usr/bin/env python3
"""Build verified English neural MP3s for the original Grade 12 Elective unit Listening tasks.
Never publish a placeholder audio file, and never claim a recording belongs to a changed script.
"""
import asyncio
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
from mutagen.mp3 import MP3
import edge_tts

ROOT = pathlib.Path(__file__).resolve().parents[1]
UNIT_DIR = ROOT / "grade12/elective/units"
AUDIO_DIR = UNIT_DIR / "audio"
VOICES = ("en-GB-SoniaNeural", "en-GB-RyanNeural")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def run_ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str,args)],check=True)

async def render_task(source, target):
    script = source["script"].strip()
    if source["skill"] == "Listening 1":
        turns = []
        speaker_names = []
        for line in script.splitlines():
            m = re.fullmatch(r"\s*([A-Za-z]+)\s*:\s*(.+)\s*", line)
            if not m:
                raise ValueError("Unexpected dialogue line: " + line[:120])
            speaker=m.group(1)
            if speaker not in speaker_names: speaker_names.append(speaker)
            if len(speaker_names)>2:raise ValueError("Dialogue has more than two speakers")
            turns.append((m.group(2).strip(),speaker_names.index(speaker)))
        if not 25 <= len(turns) <= 30:
            raise ValueError("Dialogue turns missing")
        intro = "You are going to hear a conversation between two people about an art exhibition. Choose one answer for each question. You will hear the conversation twice."
    else:
        if not 450 <= len(script.split()) <= 500:
            raise ValueError("Monologue outside SAH word range")
        solo_voice = 1 if ('male' in str(source.get("voice","")).lower() and 'female' not in str(source.get("voice","")).lower()) else 0
        turns = [(paragraph.strip().replace("\n"," "),solo_voice) for paragraph in re.split(r"\n\s*\n",script) if paragraph.strip()]
        intro = "You are going to hear an informative text about the arts. Complete the notes and short answers. You will hear the recording twice."

    with tempfile.TemporaryDirectory() as tmp:
        temp=pathlib.Path(tmp)
        audio_cache={}
        chunks=[]
        async def speak(text,voice):
            text=re.sub(r"\s+"," ",text).strip()
            if not text: return
            key=(text,voice)
            if key not in audio_cache:
                dest=temp/f"voice_{len(audio_cache):03d}.mp3"
                for attempt in range(4):
                    try:
                        await edge_tts.Communicate(text, VOICES[voice], rate="-7%").save(str(dest))
                        if dest.stat().st_size < 1000:
                            raise ValueError("TTS returned tiny response")
                        break
                    except Exception as error:
                        if attempt==3: raise
                        print("Retrying TTS:",type(error).__name__,flush=True)
                        await asyncio.sleep(2+attempt*2)
                audio_cache[key]=dest
            chunks.append(audio_cache[key])

        def pause(seconds):
            dest=temp/f"pause_{len(chunks):03d}.mp3"
            run_ffmpeg("-f","lavfi","-i","anullsrc=channel_layout=mono:sample_rate=44100",
                       "-t",str(seconds),"-c:a","libmp3lame","-b:a","96k",dest)
            chunks.append(dest)

        await speak(intro,0)
        pause(4)
        for repeat in range(2):
            for utterance,voice in turns:
                await speak(utterance,voice)
                pause(0.65 if len(turns)>6 else 1.2)
            pause(6 if repeat==0 else 3)
        paths=temp/"concat.txt"
        paths.write_text("".join("file '"+str(p.resolve()).replace("'","'\\''")+"'\n" for p in chunks))
        run_ffmpeg("-f","concat","-safe","0","-i",paths,"-ac","1","-ar","44100","-c:a","libmp3lame","-b:a","96k",target)

    duration=MP3(target).info.length
    if target.stat().st_size<25000 or duration<180:
        raise ValueError(f"Missing or unexpectedly short MP3 {target}: {duration}")
    return round(duration,2)

async def main():
    tracks=sorted(UNIT_DIR.glob("unit*-listening[12]-original-draft.json"))
    if not tracks: raise SystemExit("No approved-shape listening scripts found")
    prior={}
    if (AUDIO_DIR/'manifest.json').exists():
        prior=json.loads((AUDIO_DIR/'manifest.json').read_text())
    manifest={}
    for source_path in tracks:
        source=json.loads(source_path.read_text())
        if source.get("audioStatus") not in {"not_generated_until_content_review","generated_draft_pending_teacher_approval"}:
            raise ValueError("Unexpected state in "+source_path.name)
        actual=len(source["script"].split())
        if actual!=source["wordCount"]:
            raise ValueError(f"Script count mismatch in {source_path.name}")
        if source["skill"]=="Listening 1" and not 400<=actual<=450:raise ValueError(source_path.name)
        if source["skill"]=="Listening 2" and not 450<=actual<=500:raise ValueError(source_path.name)
        identifier=source_path.stem.replace("-original-draft","")
        out=AUDIO_DIR/(identifier+".mp3")
        digest=hashlib.sha256(source["script"].encode("utf-8")).hexdigest()
        expected_voices=list(VOICES) if source["skill"]=="Listening 1" else [VOICES[1 if ('male' in str(source.get("voice","")).lower() and 'female' not in str(source.get("voice","")).lower()) else 0]]
        previous=prior.get(source_path.name)
        if previous and previous.get('voices')==expected_voices and previous.get('scriptSha256')==digest and out.exists() and out.stat().st_size>25000 and MP3(out).info.length>180:
            duration=round(MP3(out).info.length,2)
            print("REUSE",out.relative_to(ROOT),"validated script hash",flush=True)
        else:
            duration=await render_task(source,out)
        manifest[source_path.name]={
            "sourceFile":str(source_path.relative_to(ROOT)),
            "scriptSha256":digest,
            "mp3":out.name,
            "durationSeconds":duration,
            "bytes":out.stat().st_size,
            "voices":expected_voices,
            "scriptReadTwice":True,
            "status":"neural_mp3_generated__teacher_listening_quality_approval_pending"
        }
        print("GENERATED",out.relative_to(ROOT),duration,"seconds",flush=True)
    (AUDIO_DIR/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print("All",len(tracks),"listening tracks generated; hashes and durations recorded.")

if __name__=="__main__": asyncio.run(main())
