"""Merge out1..4.json with cues.json -> captions_original.srt and captions_english.srt (YouTube-ready).
usage: python3 build_srt.py motion/work/cap motion/out/captions"""
import json, pathlib, textwrap, sys
D = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
cues = json.load(open(D / 'cues.json'))
tr = {}
for k in range(1, 5):
    for x in json.load(open(D / f'out{k}.json')): tr[x['i']] = x
missing = [c['i'] for c in cues if c['i'] not in tr or not tr[c['i']].get('orig') or not tr[c['i']].get('en')]
assert not missing, f'missing cues: {missing}'
ts = lambda t: f"{int(t//3600):02}:{int(t%3600//60):02}:{int(t%60):02},{int(round((t%1)*1000)) % 1000:03}"
def wrap(s, w=42):
    s = ' '.join(s.split())
    if len(s) <= w: return s
    sp = [i for i, ch in enumerate(s) if ch == ' ']          # break at the space closest to the middle: two balanced lines
    cut = min(sp, key=lambda i: abs(i - len(s) / 2))
    return s[:cut] + '\n' + s[cut + 1:]
for key, name in (('orig', 'captions_original.srt'), ('en', 'captions_english.srt')):
    blocks = [f"{n}\n{ts(c['s'])} --> {ts(c['e'])}\n{wrap(tr[c['i']][key])}\n" for n, c in enumerate(cues, 1)]
    (OUT / name).write_text('\n'.join(blocks), encoding='utf-8'); print('wrote', OUT / name, len(blocks), 'cues')
