#!/usr/bin/env python3
"""Download generated speech to GitHub only when valid MP3 bytes are obtained."""
import json, pathlib, urllib.request, sys
root=pathlib.Path(__file__).resolve().parents[1]
items=json.loads((root/'NATURAL_AUDIO_SOURCES.json').read_text())
failed=[]; ok=0
for x in items:
    dest=root/x['file']; dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and dest.stat().st_size>1024:
        ok+=1; continue
    try:
        req=urllib.request.Request(x['source_url'],headers={'User-Agent':'Mozilla/5.0 ExamAudioArchiver/1.0'})
        with urllib.request.urlopen(req,timeout=25) as r:
            data=r.read(10_000_001)
            if len(data)>10_000_000: raise ValueError('unexpected oversized output')
            if not (data[:3]==b'ID3' or (len(data)>2 and data[0]==255 and data[1]&224==224)):
                raise ValueError('not MP3, source may be expired')
            if len(data)<1024: raise ValueError('too short')
            dest.write_bytes(data); ok+=1
            print('OK',dest,len(data))
    except Exception as e:
        print('FAIL',x['file'],str(e),file=sys.stderr);failed.append(x['file'])
print(f'valid={ok}, failed={len(failed)}')
if failed:sys.exit(1)
