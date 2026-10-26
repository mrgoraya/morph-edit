"""Re-transcribe the gaps find_gaps.py printed. usage: motion/.venv/bin/python retx.py "<video>" "[(359.7,372.1),...]" motion/work/gapwords.json [language, default auto; e.g. en, ur]"""
import numpy as np, json, sys, ast
from faster_whisper import WhisperModel
R=16000
GAPS=ast.literal_eval(sys.argv[2])
LANG=sys.argv[4] if len(sys.argv)>4 and sys.argv[4]!='auto' else None
import subprocess
raw=subprocess.run(['ffmpeg','-v','error','-i',sys.argv[1],'-vn','-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
a=np.frombuffer(raw,np.int16).astype(np.float32)/32768
m=WhisperModel('large-v3-turbo',device='cpu',compute_type='int8')
out=[]
for s,e in GAPS:
    s0,e0=max(0,s-0.6),e+0.6
    segs,_=m.transcribe(a[int(s0*R):int(e0*R)],language=LANG,word_timestamps=True,vad_filter=False,condition_on_previous_text=False,beam_size=5)
    for sg in segs:
        for w in sg.words:
            t=s0+w.start
            if s-0.3<=t<e+0.3: out.append((round(t,2),w.word.strip()))
    print(f'{s}-{e}: {sum(1 for t,_ in out if s-0.3<=t<e+0.3)} words',flush=True)
json.dump(out,open(sys.argv[3],'w'),ensure_ascii=False)
