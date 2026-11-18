#!/usr/bin/env python3
"""Create review-only natural MP3s for six rewritten G11/G12 Core listening tasks.

Inputs are ONLY staged review JSONs; this generator never modifies live unit
bank files. Every full interview/passage is read once, then in its entirety
after "Now listen again". Voice casting uses the explicitly named speakers.
"""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from listening_voice_roles import VOICE_NAMES, parse_dialogue, voice_for_speaker

ROOT = Path(__file__).resolve().parents[1]
REVIEW_FILES = (
    ROOT / "review/g11-g12-core-listening2-unique-replacements.json",
    ROOT / "review/g11-g12-core-remaining-listening-unique.json",
)


def find_draft(grade, unit, part):
    found = []
    for path in REVIEW_FILES:
        pack = json.loads(path.read_text(encoding="utf-8"))
        if pack.get("reviewOnly") is not True:
            raise ValueError(f"Non-review input file: {path}")
        for item in pack["drafts"]:
            item_unit = item["unit"]
            number = item_unit["number"] if isinstance(item_unit, dict) else int(item_unit)
            section = int(item.get("part") or re.search(r"\d+", item["skill"]).group())
            if (item["grade"], number, section) == (grade, unit, part):
                found.append(item)
    if len(found) != 1:
        raise ValueError(f"Expected exactly one draft G{grade}/U{unit}/L{part}, found {len(found)}")
    draft = found[0]
    if draft.get("readyForStudentExam") is not False:
        raise ValueError("Only unpublished review drafts can be recorded")
    if len(draft["questions"]) != (7 if part == 1 else 8):
        raise ValueError("Question-count mismatch")
    for question in draft["questions"]:
        evidence = question.get("evidence", "")
        if not evidence or evidence.casefold() not in draft["script"].casefold():
            raise ValueError(f"Missing source evidence for question: {question['stem']}")
    return draft


def segments(draft, part):
    script = draft["script"].strip()
    if part == 1:
        cast = draft["cast"]
        turns = parse_dialogue(script, cast)
        if len(turns) < 20:
            raise ValueError("Listening 1 dialogue is unexpectedly short")
        if set(name for _, _, name in turns) != set(cast):
            raise ValueError("Speaker map does not match actual dialogue")
        return [(words, voice, name) for words, voice, name in turns]
    # "Part One" / "Part Two" are section headings, not spoken passages.
    if not re.search(r"(?im)^Part One\s*$", script) or not re.search(r"(?im)^Part Two\s*$", script):
        raise ValueError("Listening 2 must have both parts")
    speaker = draft.get("speaker") or next(iter(draft["cast"]))
    voice = voice_for_speaker(speaker, {speaker: draft.get("cast", {}).get(speaker)}
                              if draft.get("cast", {}).get(speaker) else None)
    bodies = [
        re.sub(r"(?im)^Part (?:One|Two)\s*$", "", part_text).strip()
        for part_text in re.split(r"(?im)(?=^Part Two\s*$)", script)
    ]
    if len(bodies) != 2 or any(len(x.split()) < 90 for x in bodies):
        raise ValueError("Invalid listening 2 passage segmentation")
    return [(body, voice, speaker) for body in bodies]


def run_ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)],
                   check=True)


async def produce(grade, unit, part, destination):
    import edge_tts
    from mutagen.mp3 import MP3

    draft = find_draft(grade, unit, part)
    spoken = segments(draft, part)
    voice_cast = {name: VOICE_NAMES[voice] for _, voice, name in spoken}
    output = Path(destination)
    output.mkdir(parents=True, exist_ok=True)
    stem = f"g{grade}-core-u{unit}-listening{part}"
    target = output / f"{stem}.mp3"
    events = []
    selected = set()
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        cache = {}
        files = []

        async def speak(words, index, speaker=None, pass_number=0):
            words = " ".join(words.split())
            if not words:
                return
            if index < 0 or index >= len(VOICE_NAMES):
                raise ValueError("Invalid voice index")
            key = (words, index)
            if key not in cache:
                path = temp / f"speech-{len(cache):04d}.mp3"
                await edge_tts.Communicate(words, VOICE_NAMES[index], rate="-8%").save(str(path))
                if not path.is_file() or path.stat().st_size < 1200 or MP3(path).info.length < 0.5:
                    raise ValueError("Neural voice unavailable; cannot produce review audio")
                cache[key] = path
            files.append(cache[key])
            selected.add(VOICE_NAMES[index])
            events.append({"kind": "speech", "speaker": speaker or "Announcer",
                           "voice": VOICE_NAMES[index], "pass": pass_number,
                           "text": words[:100]})

        def silence(seconds):
            path = temp / f"pause-{len(files):04d}.mp3"
            run_ffmpeg("-f", "lavfi", "-i",
                       "anullsrc=channel_layout=mono:sample_rate=44100",
                       "-t", seconds, "-c:a", "libmp3lame", "-b:a", "96k", path)
            files.append(path)

        introduction = ("Listening one. Listen to the complete interview and answer the questions."
                        if part == 1 else
                        "Listening two. Listen to the complete passage and answer the questions.")
        await speak(introduction + " You will hear it twice.", 0)
        silence(2.5)

        for reading in (1, 2):
            if reading == 2:
                await speak("Now listen again.", 0, pass_number=0)
                silence(2)
            for idx, (words, voice, speaker) in enumerate(spoken):
                await speak(words, voice, speaker, pass_number=reading)
                silence(0.7 if part == 1 else 1.5)
            silence(2)
        concat = temp / "concat.txt"
        concat.write_text("".join("file '" + str(path.resolve()).replace("'", "'\\''") + "'\n"
                                  for path in files), encoding="utf-8")
        run_ffmpeg("-f", "concat", "-safe", "0", "-i", concat, "-ac", "1",
                   "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "96k", target)

    duration = MP3(target).info.length
    if duration < 90 or target.stat().st_size < 20000:
        raise ValueError("Recording duration/size unexpectedly small")
    sequence1 = [e for e in events if e["kind"] == "speech" and e["pass"] == 1]
    sequence2 = [e for e in events if e["kind"] == "speech" and e["pass"] == 2]
    assert len(sequence1) == len(sequence2) == len(spoken)
    assert [(x["speaker"], x["voice"], x["text"]) for x in sequence1] == [
        (x["speaker"], x["voice"], x["text"]) for x in sequence2]
    assert sum(e["text"] == "Now listen again." for e in events) == 1
    source_hash = hashlib.sha256(json.dumps({
        "script": draft["script"], "questions": draft["questions"],
        "cast": voice_cast}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    manifest = {"grade": grade, "unit": unit, "track": "core", "part": part,
                "status": "audition-only-no-student-release",
                "sourceSha256": source_hash,
                "mp3": target.name, "seconds": round(duration, 2),
                "usedVoices": sorted(selected), "speakerCast": voice_cast,
                "completeReadings": 2, "voiceRoutingVersion": "identity-v2",
                "spokenPartsPerReading": len(spoken), "timeline": events}
    (output / f"{stem}.manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("PASS AUDIO", stem, "seconds", round(duration), "cast", voice_cast, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grade", type=int, choices=(11, 12), required=True)
    parser.add_argument("--unit", type=int, choices=(3, 4), required=True)
    parser.add_argument("--part", type=int, choices=(1, 2), required=True)
    parser.add_argument("--out", default="/tmp/my-exams-highgrade-audio-review")
    args = parser.parse_args()
    asyncio.run(produce(args.grade, args.unit, args.part, args.out))


if __name__ == "__main__":
    main()
