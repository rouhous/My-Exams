#!/usr/bin/env python3
"""Inventory exams and audit listening audio/image integrity from current tracked files.
Run from repository root. Asset existence and source SHA checks are automatic;
visual semantics, textbook pages, and recorded voice quality require human review.
"""
import hashlib,json,pathlib,re,collections,datetime,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
DATE="2026-11-14"
def read(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
def file(path):return (ROOT/path).is_file()
def size(path):
    p=ROOT/path
    return p.stat().st_size if p.is_file() else 0
def digest(d):
    return hashlib.sha256(json.dumps(d,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def sha(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()
failures=[];warnings=[];images=collections.defaultdict(lambda:{"optionReferences":0,"missingFiles":[],"scriptKeywordChecks":0,"scriptKeywordMatches":0,"visualApproval":"pending"})
audio=collections.defaultdict(lambda:{"requiredOriginalListeningSections":0,"verifiedLinkedMP3":0,"presentButNotSourceVerified":0,"missing":[],"reportedReusedSources":[]})
def req(g,path,detail):
    if not file(path):
        failures.append({"grade":str(g),"path":str(path),"issue":detail})
        return False
    return True
# Grades 5-6: source-level manifest hashed with transcripts and picture choices.
a56=read("grades5-6/activities.json")["activities"]
man56=read("grades5-6/audio-natural/script_audio_manifest.json")
for task in a56:
    if task.get("skill")!="listening":continue
    g=str(task["grade"]);au=audio[g];au["requiredOriginalListeningSections"]+=1
    path="grades5-6/audio-natural/"+task["id"]+".mp3"
    entry=man56.get(task["id"],{})
    fingerprint=digest({"passages":task.get("passages"),"passage":task.get("passage"),"questions":task["questions"],"pictures":task.get("pictureOptions")})
    if req(g,path,"Natural listening MP3 missing") and entry.get("sha256_of_script")==fingerprint and size(path)>15000:
        au["verifiedLinkedMP3"]+=1
    else:
        au["missing"].append({"model":task["model"],"task":task["id"],"reason":"missing_or_stale_audio_manifest"})
    if task.get("part")==1:
        opts=task.get("pictureOptions",[]);im=images[g]
        for word in opts:
            path="grades5-6/images/"+word+".svg"
            im["optionReferences"]+=1
            if not req(g,path,"Listening picture option missing"):im["missingFiles"].append(path)
        for i,q in enumerate(task["questions"]):
            word=opts[q["answer"]]
            passage=task["passages"][i].lower().replace("-"," ")
            im["scriptKeywordChecks"]+=1
            if word.replace("-"," ").lower() in passage:
                im["scriptKeywordMatches"]+=1
            else:warnings.append({"grade":g,"task":task["id"],"question":i+1,"kind":"image_answer_keyword_not_in_script","image":word})
# Grades 7-8: regenerations have a source checksum of the items, transcript and script.
models78=read("grades7-8/activities.json")
manifest78=read("grades7-8/assets/audio-natural/manifest.json") if file("grades7-8/assets/audio-natural/manifest.json") else {}
for m in models78:
    g=str(m["grade"]);au=audio[g];im=images[g]
    for s in m["sections"]:
        if s.get("key") not in ("listening1","listening2"):continue
        au["requiredOriginalListeningSections"]+=1
        key=m["id"]+"-"+s["key"]
        path="grades7-8/assets/audio-natural/"+key+".mp3"
        fp=digest({"items":s.get("items"),"script":s.get("script"),"transcript":s.get("transcript")})
        entry=manifest78.get(key,{})
        if req(g,path,"Natural listening MP3 missing") and entry.get("script_and_questions_sha256")==fp and size(path)>15000:
            au["verifiedLinkedMP3"]+=1
        else:au["missing"].append({"model":m["model"],"task":key,"reason":"missing_or_stale_audio_manifest"})
        for q in s.get("items",[]):
            if not q.get("images"):continue
            if len(q["images"])!=len(q["options"]) or not 0<=q["answer"]<len(q["images"]):
                failures.append({"grade":g,"task":key,"issue":"Picture options cannot be mapped to answers"})
            for code in q["images"]:
                path="grades7-8/assets/illustrations/"+code+".svg"
                im["optionReferences"]+=1
                if not req(g,path,"Picture asset missing"):im["missingFiles"].append(path)
# Grade 9: seven delivered models with whole-section reuse, segment voice provenance.
models9=read("grade9/data.json")["models"]
audio["9"]["sourceModelsWithListening"]=7
natu9_js=(ROOT/"grade9/natural_audio.js").read_text()
start=natu9_js.index("const NATURAL_AUDIO=")+len("const NATURAL_AUDIO=")
jdecoder=json.JSONDecoder()
cfg9,_=jdecoder.raw_decode(natu9_js[start:])
for key in ("g9-A-L1","g9-A-L2"):
    c=cfg9[key]
    for seg in [c["intro"],*c["segments"]]:
        local=(ROOT/"grade9"/seg["url"]).resolve()
        if not local.is_file() or local.stat().st_size<1000:
            failures.append({"grade":"9","task":key,"issue":"Natural segmented audio missing","url":seg["url"]})
source9={}
for m in models9:
    for t in m["tasks"]:
        if t.get("skill")!="listening":continue
        key=t["id"]
        audio["9"]["requiredOriginalListeningSections"]+=1
        source9[key]=t
        if not req(9,"grade9/"+t["audio"],"Grade 9 fallback MP3 missing"):
            audio["9"]["missing"].append(key)
        elif key.startswith("g9-A-"):
            audio["9"]["verifiedLinkedMP3"]+=1
        else:
            name={"g9-B-L1":"g9-b-listening-1.mp3","g9-B-L2":"g9-b-listening-2.mp3",
                  "g9-C-L1":"g9-c-listening-1.mp3","g9-C-L2":"g9-c-listening-2.mp3",
                  "g9-D-L1":"g9-g-listening-1.mp3","g9-D-L2":"g9-g-listening-2.mp3"}.get(key)
            if name and req(9,"grade9/audio-natural/"+name,"Grade 9 natural MP3 missing"):
                audio["9"]["presentButNotSourceVerified"]+=1
            else:audio["9"]["missing"].append(key)
        for q in t.get("items",[]):
            if not q.get("images"):continue
            if len(q["images"])!=len(q["choices"]) or not 0<=q["answer"]<len(q["choices"]):
                failures.append({"grade":"9","task":key,"issue":"Question choice and picture count mismatch"})
            for image in q["images"]:
                im=images["9"];im["optionReferences"]+=1
                path="grade9/"+image
                if not req(9,path,"Grade 9 picture missing"):im["missingFiles"].append(path)
images["9"]["visualApproval"]="pending_visual_check_of_opaque_PNG_filenames"
# Grade 10 and Grade 11 Core pilots: six natural model MP3, with hashed source passage.
for track,location,manifest_path,prefix in (
    ("10","grade10/data.json","grade10/audio/manifest.json","grade10/audio/"),
    ("11-core","grade11/core/data.json","grade11/core/audio/manifest.json","grade11/core/audio/"),
):
    models=read(location)["models"];manifest=read(manifest_path)
    for m in models:
        a=audio[track];a["requiredOriginalListeningSections"]+=1
        entry=manifest.get(m["id"],{})
        path=prefix+entry.get("mp3","__missing__.mp3")
        if req(track,path,"Model natural MP3 absent") and entry.get("passage_sha256")==sha(m["listening"]["passage"]) and size(path)>15000:
            a["verifiedLinkedMP3"]+=1
        else:a["missing"].append({"model":m["id"],"issue":"audio_absent_or_stale"})
# Grade 11 Core separate nine-section semester A paper: original 2 listening tasks need independent audio.
audio["11-core-semester-a"]["requiredOriginalListeningSections"]=2
audio["11-core-semester-a"]["missing"]=[
    {"model":"semester-paper-A","section":"Listening 1","reason":"teacher-read script only"},
    {"model":"semester-paper-A","section":"Listening 2","reason":"teacher-read script only"}
]
# Higher-grade provisional banks A-F: no verified published audio manifest at this checkpoint.
upper=read("higher_grades_corrected.json")
for track in ("11-elective","12-core","12-elective"):
    a=audio[track+"-legacy"]
    a["sourceModelsWithListening"]=len(upper[track])
    for m in upper[track]:
        for p in m["parts"]:
            if p["key"].startswith("lst"):
                a["requiredOriginalListeningSections"]+=1
                a["missing"].append({"model":m["id"],"section":p["key"],"reason":"no validated MP3 linked in source bank"})
# New Grade 12 Elective unit papers: eight independent 400-500-word listening source recordings.
unit_dir=ROOT/"grade12/elective/units"
manifest_path=unit_dir/"audio/manifest.json"
unitmanifest=json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
for unit in (1,2,3,4):
    for t in (1,2):
        task=f"unit{unit}-listening{t}-original-draft.json"
        d=read("grade12/elective/units/"+task)
        a=audio["12-elective-units"]
        a["requiredOriginalListeningSections"]+=1
        entry=unitmanifest.get(task,{})
        path="grade12/elective/units/audio/"+entry.get("mp3","__missing__.mp3")
        if file(path) and entry.get("scriptSha256")==sha(d["script"]) and size(path)>25000:
            a["verifiedLinkedMP3"]+=1
        else:a["missing"].append({"unit":unit,"listening":t,"reason":"MP3 missing or script hash stale"})
# Inventory: fixed/mixed and random clearly separated; no claim of complete teacher-approved release.
inventory={
"generated":DATE,
"scope":{"grades":[5,6,7,8,9,10,11,12],"semester":1,"excludedGrades":[1,2,3,4],"project":"My Exams"},
"tracks":[
{"grade":"5","fixedModels":4,"fixedIds":"A-D","mixedFixedModels":2,"mixedIds":"E-F","randomComplete":True,"sectionsAudioInBase":8,"audioVerified":audio["5"]["verifiedLinkedMP3"],"listeningPictures":images["5"]["optionReferences"],"certifiedComplete":False},
{"grade":"6","fixedModels":4,"fixedIds":"A-D (D mixed)","mixedFixedModels":2,"mixedIds":"E-F","randomComplete":True,"sectionsAudioInBase":8,"audioVerified":audio["6"]["verifiedLinkedMP3"],"listeningPictures":images["6"]["optionReferences"],"certifiedComplete":False},
{"grade":"7","fixedModels":4,"fixedIds":"A-D (D mixed)","mixedFixedModels":2,"mixedIds":"E-F","randomComplete":True,"sectionsAudioInBase":8,"audioVerified":audio["7"]["verifiedLinkedMP3"],"listeningPictures":images["7"]["optionReferences"],"certifiedComplete":False},
{"grade":"8","fixedModels":4,"fixedIds":"A-D (D mixed)","mixedFixedModels":2,"mixedIds":"E-F","randomComplete":True,"sectionsAudioInBase":8,"audioVerified":audio["8"]["verifiedLinkedMP3"],"listeningPictures":images["8"]["optionReferences"],"certifiedComplete":False},
{"grade":"9","fixedModels":7,"fixedIds":"A-G","mixedFixedModels":0,"mixedIds":"","randomComplete":True,"sectionsAudioInBase":14,"audioVerified":audio["9"]["verifiedLinkedMP3"],"audioNaturalHostedButNoSourceHash":audio["9"]["presentButNotSourceVerified"],"listeningPictures":images["9"]["optionReferences"],"certifiedComplete":False},
{"grade":"10","fixedModels":4,"fixedIds":"A-D","mixedFixedModels":2,"mixedIds":"E-F","randomComplete":True,"sectionsAudioInBase":6,"audioVerified":audio["10"]["verifiedLinkedMP3"],"certifiedComplete":False},
{"grade":"11 Core","fixedModels":4,"fixedIds":"A-D (5-section pilot)","mixedFixedModels":2,"mixedIds":"E-F","additionalTeacherReadSemesterPapers":1,"randomComplete":True,"legacyPilotAudio":audio["11-core"]["verifiedLinkedMP3"],"newSemesterPaperAudio":0,"certifiedComplete":False},
{"grade":"11 Elective","fixedModels":4,"fixedIds":"A-D provisional","mixedFixedModels":2,"mixedIds":"E-F","randomComplete":True,"legacyListeningMP3":0,"certifiedComplete":False},
{"grade":"12 Core","fixedModels":4,"fixedIds":"A-D provisional","mixedFixedModels":2,"mixedIds":"E-F","randomComplete":True,"legacyListeningMP3":0,"certifiedComplete":False},
{"grade":"12 Elective","fixedModels":4,"fixedIds":"A-D new unit papers","mixedFixedModels":0,"mixedIds":"","additionalLegacyDraftModels":6,"randomComplete":True,"sectionsAudioInNewUnitPapers":8,"audioVerified":audio["12-elective-units"]["verifiedLinkedMP3"],"certifiedComplete":False}
],
"notes":[
"Grade 5–8 mixed models E/F and random exams compose intact tasks from source models; no new independent MP3 required where a passage is reused with its exact answer key.",
"Grade 9 provides A–G and a regenerated R random mode; model D/E/F reuse listening sections, not new independent scripts.",
"Grade 11 Core five-section pilots cannot be treated as official nine-section semester papers; only a separate teacher-read nine-section Paper A has been authored so far.",
"Grade 12 Elective old A–F drafts coexist with four new, distinct 70-mark unit papers; only new unit papers are the basis of the new comprehensive randomized full exam.",
"Physical image availability is NOT evidence of correct subject depiction. Grade 9 PNG filenames are opaque and require visual page-level signoff.",
"Technical source matches do NOT certify official textbook page-to-unit alignment, AI writing grading, naturalness, or real phone offline playback."
]}
audit={"generated":DATE,"scope":"Grades 5–12 first-semester media, no Grades 1–4","images":dict(images),"audio":dict(audio),
       "missingPhysicalAssets":failures,"editorialReviewWarnings":warnings,
       "note":"Audio source SHA verification is stronger than presence-only. Semantic illustration and textbook alignment need teacher review."}
out1=ROOT/"MEDIA_STATUS_2026-11-14.json";out1.write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
out2=ROOT/"EXAM_INVENTORY_2026-11-14.json";out2.write_text(json.dumps(inventory,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("INVENTORY",json.dumps({"grades":len(inventory["tracks"]),"audio":{g:{k:v for k,v in a.items() if k in ("requiredOriginalListeningSections","verifiedLinkedMP3","presentButNotSourceVerified")} for g,a in audit["audio"].items()},"images":{g:i["optionReferences"] for g,i in audit["images"].items()},"physicalFailures":len(failures),"warnings":len(warnings)},ensure_ascii=False))
if failures:
    print("MISSING ASSETS",json.dumps(failures,ensure_ascii=False))
    sys.exit(1)
