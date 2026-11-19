#!/usr/bin/env python3
"""Build two-pass listening recordings from the same banks served to students."""
import asyncio
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

import edge_tts
from gtts import gTTS
from mutagen.mp3 import MP3
from listening_voice_roles import VOICE_NAMES, parse_dialogue, voice_for_narration

ROOT = Path(__file__).resolve().parents[1]
LABELS = ("one", "two", "three", "four", "five")
PROMPT = "You will hear five short texts. Listen to all five, then listen to all five again."
REPLAY = "Now listen again."


def source(path):
    return json.loads((ROOT / path).read_text())


def speaking_turns(text, hints=None, fallback=0):
    text = re.sub(r"^Text (?:one|two|three|four|five|[1-5])[. :]+", "", text, flags=re.I)
    turns = parse_dialogue(text, hints)
    if turns:
        return [(words, voice) for words, voice, _ in turns]
    return [(text, voice_for_narration(text, fallback_voice=fallback))]


def schedule(short, text=None, hints=None):
    if short:
        if len(short) != 5:
            raise ValueError("Expected precisely five numbered texts")
        numbered = []
        for index, (label, body) in enumerate(zip(LABELS, short)):
            numbered.extend([("Text " + label + ".", 0), *speaking_turns(body, hints, index % 2), 3.0])
        return [ (PROMPT, 0), 3.0, *numbered, (REPLAY, 0), 2.0, *numbered ]
    if not text:
        raise ValueError("Empty passage")
    passage = []
    for turn in speaking_turns(text, hints):
        passage.extend([turn, 0.55])
    return [("Listen to the passage. You will hear it twice.", 0), 3.0, *passage, 3.0, (REPLAY, 0), 2.0, *passage]


def tasks():
    for task in source("grades5-6/activities.json")["activities"]:
        if task["skill"] == "listening" and (task["part"] == 1 or task["id"] == "g6-d-listening-2"):
            yield "grades5-6/audio-reviewed/" + task["id"] + ".mp3", task.get("passages"), task.get("passage"), task.get("speakerGenders"), None
    for model in source("grades7-8/activities.json"):
        for task in model["sections"]:
            key = task["key"]
            if key == "listening1" or (key == "listening2" and model["model"] == "D"):
                shorts = [x["script"] for x in task["items"]] if key == "listening1" else None
                yield "grades7-8/assets/audio-reviewed/" + model["id"] + "-" + key + ".mp3", shorts, task.get("script"), task.get("speakerGenders"), None
    seen = set()
    for model in source("grade9/data.json")["models"]:
        for task in model["tasks"]:
            clip = task.get("reviewedAudio")
            if clip and clip not in seen:
                seen.add(clip)
                shorts = [x["script"] for x in task["items"]] if task["group"] == 1 else None
                yield "grade9/" + clip, shorts, task.get("transcript"), task.get("speakerGenders"), None
    for model in source("grade9/unit-exams/models.json")["models"]:
        task = model["tasks"][0]
        if task.get("group") != 1:
            raise ValueError("Unexpected order in Grade 9 unit tasks")
        clip = f"audio/g9-{model['model'].lower()}-listening-1-two-pass.mp3"
        yield "grade9/unit-exams/" + clip, [x["script"] for x in task["items"]], None, None, (task, clip)


def ff(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], check=True)


async def render(job, slots):
    path, short, body, hints, unit_track = job
    output = ROOT / path
    output.parent.mkdir(parents=True, exist_ok=True)
    plan = schedule(short, body, hints)
    async with slots:
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            clips = {}
            for segment in dict.fromkeys(plan):
                frames = directory / f"{len(clips)}.wav"
                if isinstance(segment, tuple):
                    text, voice = segment
                    mp3 = frames.with_suffix(".mp3")
                    try:
                        await asyncio.wait_for(edge_tts.Communicate(text, VOICE_NAMES[voice], rate="-8%").save(str(mp3)), 30)
                        if MP3(mp3).info.length < .25:
                            raise ValueError("Too short")
                    except Exception:
                        await asyncio.to_thread(gTTS(text, lang="en", tld="co.uk", timeout=18).save, str(mp3))
                    ff("-i", mp3, "-ar", "24000", "-ac", "1", frames)
                else:
                    ff("-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", segment, frames)
                clips[segment] = frames
            playlist = directory / "concat.txt"
            playlist.write_text("".join(f"file '{clips[x]}'\n" for x in plan))
            ff("-f", "concat", "-safe", "0", "-i", playlist, "-c:a", "libmp3lame", "-b:a", "64k", output)
    length = round(MP3(output).info.length, 2)
    if length < 40 or output.stat().st_size < 20000:
        raise ValueError(f"Invalid MP3: {path}")
    numbering = [text for text, voice in (x for x in plan if isinstance(x, tuple)) if text in {f"Text {x}." for x in LABELS}]
    if short and numbering != [f"Text {x}." for x in LABELS] * 2:
        raise ValueError(f"Bad numbering: {path}")
    order = [str(i) for i in range(1, 6)] if short else ["complete passage"]
    evidence = dict(sequence=[*order, REPLAY, *order], seconds=length, bytes=output.stat().st_size,
                    sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    print(path, evidence["sequence"], length, flush=True)
    return path, evidence, unit_track


async def main():
    slots = asyncio.Semaphore(5)
    results = await asyncio.gather(*(render(job, slots) for job in tasks()))
    manifest_path = ROOT / "grade9/unit-exams/audio/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for path, evidence, unit in results:
        if unit:
            task, clip = unit
            fingerprint = hashlib.sha256(json.dumps({key: task.get(key) for key in ("transcript", "items", "questions")}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            manifest[task["id"]] = dict(manifest[task["id"]], sourceHash=fingerprint,
                                         mp3=Path(clip).name, seconds=evidence["seconds"], bytes=evidence["bytes"],
                                         sequence=evidence["sequence"], playedTwice=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "listening-release-manifest.json").write_text(json.dumps({path: data for path, data, _ in results}, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
