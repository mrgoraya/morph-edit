"""Write index.html: every clip playing at once in a grid, plus the full preview and links to viewer/compare.
usage: python3 make_gallery.py motion/plan.json motion/out/preview.mp4   (run after make_pages.py)"""
import json, sys, pathlib, os, html
plan_p = pathlib.Path(sys.argv[1]); P = json.load(open(plan_p)); base = plan_p.parent
preview = pathlib.Path(sys.argv[2]).resolve(); out = preview.parent
fmt = lambda t: f"{int(t//60)}:{t%60:05.2f}"
def src(c):
    f = (base / c['file']).resolve()
    pv = out / (f.stem + '_preview.mp4')  # make_pages.py writes on-black previews for .mov panels
    g = pv if f.suffix.lower() == '.mov' and pv.exists() else f
    return f'{os.path.relpath(g, out)}?v={int(g.stat().st_mtime)}'  # new URL when the file changes, so browsers don't replay a cached copy
e = lambda s: html.escape(str(s))
cards = '\n'.join(f'''<article class="card"><div class="screen"><span class="spk">🔇 Click for sound</span><video src="{e(src(c))}" muted autoplay loop playsinline preload="auto"></video></div>
<div class="info"><div class="meta"><span class="num">{e(c['id'])}</span><span class="tc">{fmt(c['in'])} – {fmt(c['out'])}</span><span class="kind">{'transparent panel' if c.get('kind') == 'panel' else 'full-frame cutaway'}</span></div>
<h2>{e(c['title'])}</h2><p class="q">{e(c.get('line', ''))}</p><p class="f">{e(pathlib.Path(c['file']).name)}</p></div></article>''' for c in P['clips'])
notes = ''.join(f'<li>{e(n)}</li>' for n in P.get('notes', []))
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(P.get('title', 'Video'))} · clips</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#E9E7E2;--panel:#FFFFFF;--ink:#0B0B0B;--muted:#7D7A74;--soft:#F3F1ED;--line:#DEDAD3;--acc:#FF5A1F;--stage:#D9D6D0}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#141412;--panel:#1D1C1A;--ink:#F2F0EC;--muted:#9C9891;--soft:#262522;--line:#34322E;--stage:#0B0B0A;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#141412;--panel:#1D1C1A;--ink:#F2F0EC;--muted:#9C9891;--soft:#262522;--line:#34322E;--stage:#0B0B0A;color-scheme:dark}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 'Geist',system-ui,sans-serif}}
.wrap{{max-width:1240px;margin:0 auto;padding:28px 16px 48px;display:grid;gap:22px}}
header{{display:flex;flex-wrap:wrap;gap:10px 20px;align-items:baseline;justify-content:space-between}}
h1{{margin:0;font-size:24px;letter-spacing:-.02em}} .sub{{color:var(--muted);font-size:14px}}
nav{{display:flex;flex-wrap:wrap;gap:8px}} nav a{{color:var(--ink);text-decoration:none;font-weight:500;font-size:14px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:7px 13px}} nav a:hover{{border-color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,380px),1fr));gap:18px}}
.card{{background:var(--panel);border-radius:18px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.05),0 12px 32px -14px rgba(0,0,0,.18)}}
.card.wide{{grid-column:1/-1}} .card.live{{outline:3px solid var(--acc);outline-offset:-3px}}
.screen{{aspect-ratio:16/9;background:var(--stage);position:relative}}
.spk{{position:absolute;right:10px;top:10px;z-index:1;pointer-events:none;font-size:12.5px;font-weight:600;background:rgba(11,11,11,.72);color:#fff;border-radius:999px;padding:4px 11px}}
.card.live .spk{{background:var(--acc)}} video{{width:100%;height:100%;display:block}}
.info{{padding:14px 16px 16px;display:grid;gap:6px}}
.meta{{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:12.5px}}
.num{{font-family:'Geist Mono',monospace;background:var(--acc);color:#fff;border-radius:8px;padding:2px 8px}}
.tc{{font-family:'Geist Mono',monospace;background:var(--soft);border-radius:8px;padding:2px 8px;font-variant-numeric:tabular-nums}}
.kind{{color:var(--muted)}}
h2{{margin:0;font-size:17px;letter-spacing:-.01em}} .q{{margin:0;color:var(--muted);font-size:14px}} .f{{margin:0;font-family:'Geist Mono',monospace;font-size:12px;color:var(--muted);overflow-wrap:anywhere}}
.notes{{color:var(--muted);font-size:13.5px;max-width:80ch}} .notes ul{{margin:6px 0 0;padding-left:18px}}
</style></head><body><div class="wrap">
<header><div><h1>{e(P.get('title', 'Video'))}</h1><div class="sub">{len(P['clips'])} motion-graphic clips · click a clip to hear it with sound</div></div>
<nav><a href="viewer.html">Step through clips</a><a href="compare.html">Before / after</a><a href="TIMING.md">TIMING.md</a></nav></header>
<article class="card wide"><div class="screen"><video src="{e(preview.name)}?v={int(preview.stat().st_mtime)}" controls playsinline preload="metadata"></video></div>
<div class="info"><h2>Full preview · your video with every clip cut in</h2><p class="q">For review. For the final cut, place the clips in your editor at the timecodes below.</p></div></article>
<section class="grid">{cards}</section>
<div class="notes"><strong>What's illustrative</strong><ul>{notes}</ul></div>
</div>
<script>
const vs=[...document.querySelectorAll('.grid video')];
vs.forEach(v=>{{v.style.cursor='pointer'; v.title='Click for sound';
  v.addEventListener('click',()=>{{const on=v.muted; vs.forEach(o=>o.muted=true); v.muted=!on; if(on){{v.currentTime=0;}} const mark=()=>vs.forEach(o=>{{const c=o.closest('.card'); c.classList.toggle('live',!o.muted); c.querySelector('.spk').textContent=o.muted?'🔇 Click for sound':'🔊 Sound on · click to mute';}}); v.play().then(mark).catch(()=>{{v.muted=true; v.play(); mark();}});}});}});
</script>
</body></html>'''
open(out / 'index.html', 'w', encoding='utf-8').write(page); print('wrote', out / 'index.html')
