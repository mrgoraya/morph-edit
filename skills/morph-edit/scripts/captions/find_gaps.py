"""Find stretches where the speaker talks but the transcript has no words (Whisper drops these on long Urdu videos).
usage: motion/.venv/bin/python find_gaps.py motion/work/words.txt "<video>"   -> prints [(start,end),...] to paste into retx.py GAPS"""
import sys, subprocess, numpy as np
W = sorted(float(p.split(':', 1)[0]) for l in open(sys.argv[1]) for p in l.split())
R = 16000; raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[2], '-vn', '-ac', '1', '-ar', str(R), '-f', 's16le', '-'], capture_output=True).stdout
v = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; h = int(.05 * R); n = len(v) // h
act = 10 * np.log10(np.maximum((v[:n * h].reshape(n, h) ** 2).mean(1), 1e-12)) > -32
edges = [0.0] + W + [len(v) / R]; gaps = []
for a, b in zip(edges[:-1], edges[1:]):
    if b - a > 2.5 and act[int(a / .05):int(b / .05)].mean() > 0.3: gaps.append((round(a, 1), round(b, 1)))
print(gaps); print(len(gaps), 'gaps,', round(sum(b - a for a, b in gaps), 1), 's of speech missing')
