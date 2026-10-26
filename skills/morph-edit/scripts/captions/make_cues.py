"""words.txt (+ gapwords.json from retx.py) -> caption cues (key "orig" = the words as spoken) (<=10 words, <=~4.5 s, break on 0.7 s pauses) + 4 chunks for parallel translation.
usage: python3 make_cues.py motion/work/words.txt motion/work/gapwords.json motion/work/cap"""
import json, sys, pathlib
out = pathlib.Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
W = [(float(t), w) for l in open(sys.argv[1]) for t, w in (p.split(':', 1) for p in l.split())]
if len(sys.argv) > 2 and pathlib.Path(sys.argv[2]).exists(): W += [tuple(x) for x in json.load(open(sys.argv[2]))]
W.sort(); D = []
for t, w in W:
    if D and abs(D[-1][0] - t) < 0.08 and D[-1][1] == w: continue
    D.append((t, w))
cues, cur = [], []
for i, (t, w) in enumerate(D):
    nxt = D[i + 1][0] if i + 1 < len(D) else t + 0.6; cur.append((t, w))
    if nxt - t > 0.7 or len(cur) >= 10 or cur[-1][0] - cur[0][0] > 4.2:
        cues.append({'i': len(cues) + 1, 's': round(cur[0][0], 2), 'e': round(max(min(nxt, t + 0.9), cur[0][0] + 1.0), 2), 'orig': ' '.join(x for _, x in cur)}); cur = []
for a, b in zip(cues, cues[1:]): a['e'] = min(a['e'], b['s'] - 0.02)
json.dump(cues, open(out / 'cues.json', 'w'), ensure_ascii=False, indent=0)
k = (len(cues) + 3) // 4
for j in range(4): json.dump(cues[j * k:(j + 1) * k], open(out / f'chunk{j + 1}.json', 'w'), ensure_ascii=False, indent=0)
print(len(D), 'words ->', len(cues), 'cues in 4 chunks')
