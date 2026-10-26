"""Audio/video -> real word timestamps (faster-whisper). Use when there is no transcript, or to replace SRT estimates.
Writes words.txt in the same format as words.py (one line per segment, `time:word` pairs) and a matching transcript.srt.
usage: motion/.venv/bin/python transcribe.py motion/work/source.mp4 motion/work [model] [language] [novad]
  model default: small (use large-v3-turbo for Urdu/Hindi or mixed-language speech); language e.g. ur, en; novad keeps quiet stretches"""
import sys, os
from faster_whisper import WhisperModel
src, out = sys.argv[1], sys.argv[2]; model = sys.argv[3] if len(sys.argv) > 3 else 'small'
lang = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != 'auto' else None; vad = 'novad' not in sys.argv[5:]
os.makedirs(out, exist_ok=True)
segs, info = WhisperModel(model, device='cpu', compute_type='int8').transcribe(src, word_timestamps=True, vad_filter=vad, language=lang)
def srt(t): h, r = divmod(t, 3600); m, s = divmod(r, 60); return f'{int(h):02}:{int(m):02}:{int(s):02},{int(round((s % 1) * 1000)):03}'
lines, cues = [], []
for i, s in enumerate(segs, 1):
    lines.append(' '.join(f'{w.start:.2f}:{w.word.strip()}' for w in s.words))
    cues.append(f'{i}\n{srt(s.start)} --> {srt(s.end)}\n{s.text.strip()}\n')
open(f'{out}/words.txt', 'w').write('\n'.join(lines) + '\n')
open(f'{out}/transcript.srt', 'w').write('\n'.join(cues))
print(f'language={info.language} segments={len(cues)} -> {out}/words.txt, {out}/transcript.srt')
