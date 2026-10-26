"""UI sound effects synced to each clip's animation cues, synthesised locally (no samples, no licensing).
Reads "sfx": [[clip-local time, kind], ...] per clip in plan.json. Kinds: click pop tick type toggle pickup drop whoosh rise fall success shutter.
- writes out/sfx/<clip>_sfx.wav (SFX alone, for mixing in your editor)
- muxes the SFX into each clip file as its audio track (video stream copied, not re-encoded)
- rebuilds preview.mp4's audio as the source audio + every clip's SFX at its in-point (idempotent)
usage: python3 sfx.py motion/plan.json motion/out/preview.mp4 [sfx gain dB, default -10: effects sit ~10 dB under the voice]   (run after composite.py)"""
import json, sys, pathlib, subprocess, wave, os
import numpy as np
R = 48000
plan_p = pathlib.Path(sys.argv[1]); P = json.load(open(plan_p)); base = plan_p.parent
preview = pathlib.Path(sys.argv[2]).resolve(); gain = 10 ** ((float(sys.argv[3]) if len(sys.argv) > 3 else -10.0) / 20)  # default -10 dB: UI sounds sit well under the voice
sfx_dir = preview.parent / 'sfx'; sfx_dir.mkdir(exist_ok=True)
rng = np.random.default_rng(7)
t_ = lambda d: np.arange(int(d * R)) / R
env = lambda n, a, d: np.minimum(np.arange(n) / max(1, a * R), 1) * np.exp(-np.arange(n) / (d * R))
def glide(f0, f1, d):  # sine with exponential pitch glide
    t = t_(d); f = f0 * (f1 / f0) ** (t / d); return np.sin(2 * np.pi * np.cumsum(f) / R)
def lp(x, a):  # one-pole low-pass; a can be an array (sweeping cutoff)
    y = np.empty_like(x); v = 0.0; a = np.broadcast_to(a, x.shape)
    for i in range(len(x)): v += a[i] * (x[i] - v); y[i] = v
    return y
def noise(d): return rng.standard_normal(int(d * R))
def click(v=1.0, f=2400):
    d = 0.07; n = int(d * R); t = t_(d)
    s = np.sin(2 * np.pi * f * t) * env(n, 0.0005, 0.012) + 0.8 * np.sin(2 * np.pi * f * 0.42 * t) * env(n, 0.001, 0.02) + 0.6 * lp(noise(d), 0.5) * env(n, 0.0002, 0.004)
    return 0.6 * v * s
def pop(): d = 0.09; return 0.45 * glide(1100, 520, d) * env(int(d * R), 0.002, 0.025)
def tick(): return click(0.7, 2800)
def typ(): return click(0.55 + 0.15 * rng.random(), 1600 + 800 * rng.random())
def toggle(): a = click(0.8, 2000); b = np.zeros(int(0.05 * R)); b[:len(a)] += click(0.5, 2800)[:len(b)]; return np.concatenate([a, b])
def pickup(): d = 0.14; return 0.6 * glide(440, 880, d) * env(int(d * R), 0.004, 0.05)
def drop(): d = 0.14; n = int(d * R); return 0.5 * glide(620, 300, d) * env(n, 0.002, 0.04) + 0.35 * np.sin(2 * np.pi * 90 * t_(d)) * env(n, 0.002, 0.03)
def whoosh():
    d = 0.34; n = int(d * R); u = np.arange(n) / n
    s = lp(noise(d), 0.03 + 0.22 * np.sin(np.pi * u) ** 2); return 0.45 * s * np.sin(np.pi * u) ** 1.6  # soft: sits ~4 dB under the clicks
def rise(): d = 0.3; return 0.45 * glide(300, 700, d) * np.sin(np.pi * np.arange(int(d * R)) / int(d * R))
def fall(): d = 0.3; return 0.45 * glide(700, 280, d) * np.sin(np.pi * np.arange(int(d * R)) / int(d * R))
def success():
    out = np.zeros(int(0.42 * R))
    for k, f in enumerate([880, 1320]):
        n = int(0.3 * R); s = (np.sin(2 * np.pi * f * t_(0.3)) + 0.25 * np.sin(4 * np.pi * f * t_(0.3))) * env(n, 0.004, 0.09)
        o = int(k * 0.11 * R); out[o:o + n] += 0.45 * s
    return out
def shutter():
    out = np.zeros(int(0.07 * R)); a = click(0.6, 1500)
    for o in (0, int(0.035 * R)): out[o:o + len(a)] += a[:len(out) - o]
    return out + 0.08 * lp(noise(0.07), 0.3) * env(len(out), 0.001, 0.02)
KIND = dict(click=click, pop=pop, tick=tick, type=typ, toggle=toggle, pickup=pickup, drop=drop, whoosh=whoosh, rise=rise, fall=fall, success=success, shutter=shutter)
def write(path, x):
    x = np.clip(x, -1, 1); pcm = (x * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(R); w.writeframes(pcm.tobytes())
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)], capture_output=True, text=True).stdout)
tracks = []
for c in P['clips']:
    f = (base / c['file']).resolve(); T = dur(f); buf = np.zeros(int((T + 0.6) * R))
    for t, k in c.get('sfx', []):
        s = KIND[k](); o = int(t * R); buf[o:o + len(s)] += s[:len(buf) - o]
    buf = np.tanh(2.2 * buf[:int(T * R)] * gain) * 0.5  # soft limiter: lifts quiet transients; clips land near -16 LUFS, peaks under -5 dBFS
    wav = sfx_dir / (f.stem + '_sfx.wav'); write(wav, buf); tracks.append((c['in'], wav))
    tmp = f.with_name(f.stem + '.tmp' + f.suffix)
    acodec = ['-c:a', 'pcm_s16le'] if f.suffix.lower() == '.mov' else ['-c:a', 'aac', '-b:a', '192k']
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(f), '-i', str(wav), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', *acodec, '-shortest', str(tmp)], check=True)
    os.replace(tmp, f); print('sfx ->', f.name, f"({len(c.get('sfx', []))} cues)")
# preview: source audio + all SFX at their in-points (rebuilt from the source each time, so re-running never stacks)
src = (base / P['video']).resolve(); cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-i', str(preview), '-i', str(src)]
fc = []
for i, (tin, wav) in enumerate(tracks, 2):
    cmd += ['-i', str(wav)]; fc.append(f'[{i}:a]aresample={R},adelay={int(tin * 1000)}:all=1,volume=0.8[s{i}]')
mus = [(base / P['music']).resolve()] if P.get('music') and (base / P['music']).exists() else []  # optional background music bed (music.py), already levelled
for j, m in enumerate(mus, len(tracks) + 2): cmd += ['-i', str(m)]; fc.append(f'[{j}:a]aresample={R}[s{j}]')
k = len(tracks) + len(mus)
fc.append('[1:a]' + ''.join(f'[s{i}]' for i in range(2, k + 2)) + f'amix=inputs={k + 1}:duration=first:normalize=0,alimiter=limit=0.8:level=false[a]')
tmp = preview.with_name(preview.stem + '.tmp.mp4')
subprocess.run(cmd + ['-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(tmp)], check=True)
os.replace(tmp, preview); print('sfx mixed under the voice ->', preview.name)
