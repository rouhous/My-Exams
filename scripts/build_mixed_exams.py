#!/usr/bin/env python3
"""Normalize the published semester-one unit banks for mixed exam assembly."""
import hashlib
import json
import posixpath
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mixed-exams"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def inline(path, element):
    html = (ROOT / path).read_text(encoding="utf-8")
    return json.loads(re.search(r'<script[^>]*id="' + element + r'"[^>]*>(.*?)</script>', html, re.S)[1])


def listed_files():
    return set(subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT, text=True).split("\0"))


FILES = listed_files()
TIMING = read("mixed-exams/numbered-audio.json")
ENGLISH_MARKS = {5: 40, 6: 40, 7: 40, 8: 40, 9: 40, 10: 60, 11: 60, 12: 70}
TF = ["True", "False"]


def existing(path):
    assert path in FILES, path
    return path


def section(key, marks, questions=None, **fields):
    if questions is not None:
        assert len(questions) >= marks, (key, marks, len(questions))
        fields["questions"] = questions
    return dict(key=key, marks=marks, **fields)


def question(raw, **fields):
    q = {k: raw[k] for k in ("stem", "options", "answer", "answers", "maxWords", "rule", "explanation") if k in raw}
    if "choices" in raw:
        q["options"] = raw["choices"]
    if isinstance(q.get("answer"), bool) or q.get("answer") in TF:
        q.update(options=TF, answer=(0 if q["answer"] is True else 1) if isinstance(q["answer"], bool) else TF.index(q["answer"]))
    q["kind"] = raw.get("type") or ("mc" if "options" in q else "short")
    if q.get("options") == TF:
        q["kind"] = "tf"
    return {**q, **fields}


def writing(key, marks, raw, **fields):
    prompt = raw.get("prompt", raw.get("topic"))
    minimum = re.search(r"(?:at least|minimum)\s+(\d+)\s+words", prompt, re.I)
    return section(key, marks, prompt=prompt, minWords=raw.get("minWords", int(minimum[1]) if minimum else None),
                   **{k: raw[k] for k in ("chart", "survey", "facts") if k in raw}, **fields)


def section_audio(path, transcript, **fields):
    name = posixpath.basename(path)
    return dict(audio=existing(path), script=transcript,
                **({"timing": TIMING[name]} if name in TIMING else {}), **fields)


def image56(name):
    prefix = "grades5-6/images/" + name
    return existing(prefix + (".webp" if prefix + ".webp" in FILES else ".svg"))


def cloze(raw, items):
    passage = raw["passage"]
    markers = list(re.finditer(r"\((\d+)\)\s*_{2,}|\[(\d+)\]", passage))
    assert len(markers) == len(items), passage
    chunks = re.split(r"\n+|(?<=[.!?])\s+(?=[A-Z‘“])", passage)
    sentences = {}
    for chunk in chunks:
        gaps = list(re.finditer(r"\((\d+)\)\s*_{2,}|\[(\d+)\]", chunk))
        for target in gaps:
            current = int(target[1] or target[2]) - 1

            def replace(m):
                index = int(m[1] or m[2]) - 1
                item = items[index]
                return "_____" if current == index else (item.get("choices") or item["options"])[item["answer"]]

            context = chunk
            if re.match(r"^[\w -]+: ", chunk):
                lines = passage.splitlines()
                line_index = next(i for i, line in enumerate(lines) if chunk in line) if "\n" in passage else -1
                if line_index >= 0:
                    context = "\n".join(lines[max(0, line_index - 1):line_index + 2])
            sentences[current] = re.sub(r"\((\d+)\)\s*_{2,}|\[(\d+)\]", replace, context)
    return [question(item, stem=sentences[i]) for i, item in enumerate(items)]


def vocabulary(rows):
    return [question(dict(stem=stem, options=list(options), answer=0)) for stem, *options in rows]


# These units need additional lexical questions for a separate five-item vocabulary
# component. The sentence contexts use the published unit vocabulary and themes.
WORDS9 = [
    [("Even when meeting new pupils, Rashid is _____ enough to introduce himself.", "confident", "selfish", "careless"),
     ("An accurate _____ includes a person's interests and some basic information.", "profile", "timetable", "receipt"),
     ("At home, weaving baskets is a family _____ passed down for generations.", "tradition", "decision", "direction"),
     ("Layla paints for pleasure because watercolour painting is her favourite _____.", "hobby", "subject", "rule"),
     ("We learn more about someone's _____ by noticing how they behave towards others.", "personality", "appearance", "address")],
    [("Our class spoke to pupils in another town during a live _____.", "video call", "poster", "timetable"),
     ("The journalist asked several questions during the _____.", "interview", "announcement", "invitation"),
     ("The _____ was too far from the speaker, so the recording was hard to hear.", "microphone", "printer", "projector"),
     ("Hana could not read the message until she saw its _____ in English.", "translation", "signature", "address"),
     ("The visitor used hand movements to communicate in _____.", "sign language", "handwriting", "eye contact")],
    [("The engineers tested a _____ before making the final version of the device.", "prototype", "receipt", "headline"),
     ("The door opens when a _____ detects movement nearby.", "sensor", "charger", "keyboard"),
     ("The package was carried across the valley by a flying _____.", "drone", "router", "robotic vacuum"),
     ("The family set the _____ to turn down the heating at night.", "thermostat", "camera", "microphone"),
     ("A _____ has a strap and can record steps while you wear it.", "smartwatch", "laptop", "projector")],
]
WORDS11 = {
    3: [("A local _____ showed visitors the safest route through the old town.", "guide", "passenger", "driver"),
        ("The fort became a popular tourist _____ after it reopened.", "attraction", "reservation", "departure"),
        ("We booked our _____ early so that we would have a room near the beach.", "accommodation", "transport", "itinerary"),
        ("Before the trip, we received an _____ listing the places and times of our visits.", "itinerary", "souvenir", "passport"),
        ("The museum protects the region's cultural _____ for future generations.", "heritage", "traffic", "luggage")],
    4: [("The team built a working _____ to test its idea before production.", "prototype", "diagram", "receipt"),
        ("A _____ detects movement and switches on the lights automatically.", "sensor", "battery", "screen"),
        ("The club hopes its latest _____ will reduce the amount of water wasted.", "invention", "competition", "invitation"),
        ("The engineers used feedback to _____ the design after the first trial.", "improve", "replace", "advertise"),
        ("Recharging a _____ supplies the portable device with power again.", "battery", "switch", "screen")],
}
WORDS12 = {
    4: [("Passengers checked the _____ to find out when the next train would leave.", "timetable", "passport", "brochure"),
        ("The plane's _____ was delayed because of heavy fog.", "departure", "destination", "luggage"),
        ("We had to change trains halfway through our _____ to Muscat.", "journey", "station", "terminal"),
        ("Regular _____ often travel to work on the same bus each morning.", "commuters", "pilots", "tour guides"),
        ("The railway _____ is the place beside the tracks where passengers wait to board.", "platform", "ticket office", "car park")],
}


def foundations():
    data = inline("grades5-6/index.html", "bank")["activities"]
    for grade, count in ((5, 4), (6, 3)):
        units = []
        for i, model in enumerate("ABCD"[:count], 1):
            sections = []
            for task in [t for t in data if (t["grade"], t["model"]) == (grade, model)]:
                skill, part, fmt = task["skill"], task["part"], task["format"]
                key = skill if skill in ("grammar", "vocabulary") else skill + str(part)
                if skill == "writing":
                    sections.append(writing(key, 5, task, images=[image56(x) for x in task.get("pictureOptions", [])]))
                    continue
                qs = [question(q) for q in task["questions"]]
                extra = {}
                if fmt == "picture-match":
                    pictures = [image56(x) for x in task["pictureOptions"]]
                    extra.update(grid="images", options=pictures)
                    for q in qs:
                        q.update(target=pictures[q["answer"]])
                elif fmt == "picture-word-match":
                    words = task["wordOptions"]
                    extra.update(grid="words", options=words)
                    for n, q in enumerate(qs):
                        q.update(picture=image56(task["pictureOptions"][n]), target=words[q["answer"]])
                elif fmt == "picture-spelling":
                    for n, q in enumerate(qs):
                        q.update(picture=image56(task["pictureOptions"][n]), maxWords=1, stem="Write the word.")
                elif fmt == "text-match":
                    texts = [p["stem"] for p in task["passages"]]
                    # The statement and the three source texts form one matching item.
                    for q in qs:
                        q.update(options=texts, kind="match")
                if skill == "listening":
                    folder = "audio-reviewed" if part == 1 else "audio-natural"
                    extra.update(section_audio(f"grades5-6/{folder}/{task['id']}.mp3", task.get("passage", "")))
                    if part == 1:
                        for q, script in zip(qs, task["passages"], strict=True):
                            q["script"] = script
                elif task.get("passage"):
                    extra["passage"] = task["passage"]
                sections.append(section(key, 5, qs, **extra))
            units.append(dict(unit=i, sections=sections))
        yield str(grade), 90, units


LEXICAL78 = {
    7: [[2, 3, 7, 9], [1, 2, 8, 9], [3, 6, 7]],
    8: [[4, 5, 6, 7, 9], [2, 3, 7], [0, 1, 2, 4, 7]],
}


def middle():
    for grade in (7, 8, 9):
        units = []
        if grade == 9:
            data = read("grade9/unit-exams/models.json")["models"]
            manifest = read("grade9/unit-exams/audio/manifest.json")
        else:
            data = [m for m in inline("grades7-8/index.html", "DATA") if m["grade"] == grade and m["model"] in "ABC"]
        for i, model in enumerate(data, 1):
            sections = []
            for n, task in enumerate(model.get("sections", model.get("tasks"))):
                key = ["listening1", "listening2", "grammarvocabulary", "reading1", "reading2", "writing1", "writing2"][n]
                marks = task["marks"]
                raw = task.get("items", [])
                if n < 2:
                    if grade == 9:
                        entry = manifest[task["id"]]
                        assert entry["sourceTranscriptSha256"] == sha(task["transcript"])
                        media = "grade9/unit-exams/audio/" + entry["mp3"]
                        images = lambda refs: [existing(posixpath.normpath("grade9/unit-exams/" + x)) for x in refs]
                    else:
                        media = "grades7-8/assets/" + ("audio-reviewed/" if n == 0 else "audio-natural/") + posixpath.basename(task["audio"])
                        images = lambda refs: [existing("grades7-8/assets/illustrations/" + x + ".webp") for x in refs]
                    qs = [question(q, **({"images": images(q["images"]), "script": q["script"]} if n == 0 else {})) for q in raw]
                    sections.append(section(key, marks, qs, **section_audio(media, task["transcript"] if grade == 9 else task.get("script", ""))))
                elif n == 2:
                    gaps = cloze(task, raw)
                    if grade == 9:
                        gqs, vqs = gaps, vocabulary(WORDS9[i - 1])
                    else:
                        vocab_indices = LEXICAL78[grade][i - 1]
                        gqs = [q for j, q in enumerate(gaps) if j not in vocab_indices]
                        vqs = [q for j, q in enumerate(gaps) if j in vocab_indices]
                    # The overall section is ten marks, with five items from each strand.
                    sections.append(dict(key="grammar", marks=5, questions=gqs))
                    sections.append(dict(key="vocabulary", marks=5, questions=vqs))
                elif n == 3:
                    if grade == 9:
                        opts = [re.sub(r"^[A-E]:\s*", "", x) for x in task["options"]]
                        qs = [question(q, options=opts, stem=re.sub(r"^Person \d+:\s*", "", q["stem"]), kind="match") for q in raw]
                    else:
                        qs = [question(dict(stem=txt, options=task["continuations"], answer=a), kind="match")
                              for txt, a in zip(task["texts"], task["answers"], strict=True)]
                    sections.append(section(key, marks, qs))
                elif n == 4:
                    sections.append(section(key, marks, [question(q) for q in raw], passage=task["passage"]))
                else:
                    sections.append(writing(key, marks, task))
            units.append(dict(unit=i, sections=sections))
        yield str(grade), 120, units


def sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def grade10():
    units = []
    manifest = read("grade10/audio/manifest.json")
    for i, model in enumerate(read("grade10/data.json")["models"][:4], 1):
        ls = model["listening"]
        entry = manifest[model["id"]]
        assert entry["passage_sha256"] == sha(ls["passage"])
        sections = [section("listening", 15, [question(q) for q in ls["questions"]],
                            **section_audio("grade10/audio/" + entry["mp3"], ls["passage"]))]
        for key, marks in [("vocabulary", 5), ("grammar", 5), ("reading1", 10), ("reading2", 10)]:
            part = model[key]
            sections.append(section(key, marks, [question(q) for q in part["questions"]],
                                    **({"passage": part["passage"]} if "passage" in part else {})))
        sections += [writing("writing1", 5, model["writing1"]), writing("writing2", 10, model["writing2"])]
        units.append(dict(unit=i, sections=sections))
    yield "10", 150, units


def upper():
    for grade in (11, 12):
        for track in ("core", "elective"):
            base = f"grade{grade}/{track}/units/"
            manifest = read(base + "audio/manifest.json")
            units = []
            for i, model in enumerate("abcd", 1):
                prefix = f"unit{i}-"
                sections = []
                for n in (1, 2):
                    name = prefix + f"listening{n}-original-draft.json"
                    entry = manifest[name]
                    src = read(base + name)
                    assert entry["scriptReadTwice"] and entry["scriptSha256"] == sha(src["script"]), base + name
                    sections.append(section("listening" + str(n), src["marks"], [question(q) for q in src["questions"]],
                                            **section_audio(base + "audio/" + entry["mp3"], src["script"])))
                if track == "elective":
                    for n in (1, 2):
                        p = read(base + prefix + f"reading{n}-original-draft.json")
                        sections.append(section("reading" + str(n), p["marks"], [question(q) for q in p["questions"]], passage=p["passage"]))
                    p = read(base + prefix + "writing-original-draft.json")
                    sections.extend(writing(key, p["writing" + str(n)]["marks"], p["writing" + str(n)])
                                    for n, key in ((1, "writing1"), (2, "writing2")))
                else:
                    p = read(base + prefix + f"paper-{model}.json")["sections"]
                    for source, key in [("grm", "grammar"), ("vcb", "vocabulary"), ("rdg1", "reading1"),
                                        ("rdg2", "reading2"), ("rdg3", "reading3"), ("wrt1", "writing1"), ("wrt2", "writing2")]:
                        s = p[source]
                        if key.startswith("writing"):
                            parts = writing(key, s["marks"], s)
                        elif source == "rdg1":
                            qs = [question(q, stem=t["statement"], passage=t["passage"]) for q, t in zip(s["questions"], s["texts"], strict=True)]
                            parts = section(key, s["marks"], qs)
                        elif source in ("grm", "vcb"):
                            lexical = (WORDS11 if grade == 11 else WORDS12).get(i) if source == "vcb" else None
                            qs = vocabulary(lexical) if lexical else cloze(s, s["questions"])
                            parts = section(key, s["marks"], qs)
                        else:
                            parts = section(key, s["marks"], [question(q) for q in s["questions"]], passage=s["passage"])
                        sections.append(parts)
                units.append(dict(unit=i, sections=sections))
            yield f"{grade}-{track}", 150 if grade == 11 else 180, units


# A fixed or random paper tests distinct grammar points even when different
# unit lessons contain near-identical questions on the same form.
GRAMMAR_POINTS = {
    "5": [
        "comparative superlative participle comparative superlative",
        "past-simple past-negative past-question past-ability past-simple",
        "future-prediction future-negative wh-question future-prediction wh-question",
        "relative-clause relative-clause relative-clause obligation no-obligation",
    ],
    "6": [
        "present-simple present-continuous present-simple present-continuous present-simple",
        "past-ability past-obligation comparative-adverb past-ability past-obligation",
        "past-continuous relative-clause relative-clause past-continuous relative-clause",
    ],
    "7": [
        "present-perfect duration arrangement present-perfect verb-pattern arrangement",
        "possibility conditional modal-complement possibility conditional present-simple",
        "timetable future-plan timetable conditional future-prediction future-plan future-prediction",
    ],
    "8": [
        "past-simple obligation reported-instruction reported-question advice",
        "past-perfect past-perfect reflexive reflexive past-perfect contrast reflexive",
        "first-conditional second-conditional second-conditional zero-conditional second-conditional",
    ],
    "9": [
        "present-simple present-simple present-continuous present-continuous word-form present-simple present-simple present-continuous present-simple preposition",
        "past-simple past-continuous past-simple infinitive gerund past-simple past-simple preposition preposition past-perfect",
        "future-plan arrangement timetable prediction future-evidence conditional suggestion future-plan phrasal-verb phrasal-verb",
    ],
    "10": [
        "comparative phrasal-verb comparative-adverb phrasal-verb comparative",
        "reason conditional future-result result purpose",
        "contrast concession time-clause adjective-suffix purpose",
        "passive degree-adverb passive focusing-adverb passive",
    ],
    "11-core": [
        "past-continuous present-perfect past-simple advice conditional",
        "past-continuous past-simple advice past-simple conditional",
        "past-continuous present-perfect past-simple advice conditional",
        "past-continuous present-perfect past-simple advice conditional",
    ],
    "12-core": [
        "past-simple past-be past-negative passive conditional",
        "past-continuous present-perfect future-plan advice conditional",
        "past-continuous present-perfect past-simple advice conditional",
        "past-continuous present-perfect past-simple advice conditional",
    ],
}


def label_grammar(ident, units):
    if ident not in GRAMMAR_POINTS:
        return
    for unit, points in zip(units, GRAMMAR_POINTS[ident], strict=True):
        questions = next(s for s in unit["sections"] if s["key"] == "grammar")["questions"]
        if ident == "10" and unit["unit"] == 2:
            questions[1] = question(dict(stem="If people save energy at home, they _____ less electricity.",
                                         options=["will use", "used", "would have used", "have used"], answer=0))
        if ident == "10" and unit["unit"] == 3:
            questions[1] = question(dict(stem="_____ the weather was cloudy, the solar panels still produced electricity.",
                                         options=["Although", "Therefore", "Because of", "So that"], answer=0))
            questions[3] = question(dict(stem="Wind power is a _____ energy source because the wind is naturally replenished.",
                                         options=["renewable", "renew", "renewal", "renewing"], answer=0))
        for q, point in zip(questions, points.split(), strict=True):
            q["point"] = point


def main():
    for ident, minutes, units in (*foundations(), *middle(), *grade10(), *upper()):
        label_grammar(ident, units)
        grade = int(ident.split("-")[0])
        marks = ENGLISH_MARKS[grade]
        shapes = [[(s["key"], s["marks"]) for s in u["sections"]] for u in units]
        assert all(x == shapes[0] for x in shapes), (ident, shapes)
        assert sum(n for _, n in shapes[0]) == marks, (ident, shapes[0])
        for unit in units:
            for s in unit["sections"]:
                for q in s.get("questions", []):
                    assert q.get("stem"), (ident, q)
                    if "options" in q:
                        assert type(q["answer"]) is int and 0 <= q["answer"] < len(q["options"]), (ident, q)
                    elif "target" not in q:
                        assert q.get("answer") or q.get("answers"), (ident, q)
        bank = dict(grade=grade, minutes=minutes, marks=marks, units=units)
        (OUT / f"{ident}.json").write_text(json.dumps(bank, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        print(ident, len(units), marks, flush=True)


if __name__ == "__main__":
    main()
