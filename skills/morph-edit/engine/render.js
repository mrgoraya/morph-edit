// NODE_PATH=motion/node_modules node render.js dist/clip.html out/clip.(mp4|mov) [fps, e.g. 30000/1001 | 25 | 60]
// 4 subframes per frame across a 180° shutter, blended with ffmpeg tmix. Alpha clips -> ProRes 4444 .mov
// RENDER_SAFE=1: write frames to disk in 2 s chunks instead of piping PNGs (use for heavy full-frame pages, e.g. Shorts: the pipe can drop frames)
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');
(async()=>{
 const [html,out,fpsArg]=process.argv.slice(2); const FPS=!fpsArg?30000/1001:(fpsArg.includes('/')?fpsArg.split('/')[0]/fpsArg.split('/')[1]:+fpsArg);
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('file://'+path.resolve(html)+'?render');await p.evaluate(()=>document.fonts.ready);
 const info=await p.evaluate(()=>({T:window.DURATION,W:document.getElementById('stage').offsetWidth,H:document.getElementById('stage').offsetHeight,alpha:document.documentElement.classList.contains('alpha')}));
 await p.setViewportSize({width:info.W,height:info.H});
 const N=Math.round(info.T*FPS), K=4, sub=1/(FPS*2*K);
 const fr=(fpsArg&&fpsArg.includes('/'))?[fpsArg,`${fpsArg.split('/')[0]*4}/${fpsArg.split('/')[1]}`]:(FPS===30000/1001?['30000/1001','120000/1001']:[String(FPS),String(FPS*4)]);
 const vf=`format=gbrap,tmix=frames=4:weights='1 1 1 1',select='eq(mod(n\\,4)\\,3)',setpts=N/(${fr[0]})/TB`;
 const enc=info.alpha?['-c:v','prores_ks','-profile:v','4','-pix_fmt','yuva444p10le','-vendor','apl0']:['-c:v','libx264','-crf','14','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart'];
 if(process.env.RENDER_SAFE){   // write subframes to disk in chunks: no PNG-stream mis-splits (dropped frames on heavy full-frame pages)
  const fs=require('fs'),os=require('os');const {execFileSync}=require('child_process');
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'rs'));const CH=120;const segs=[];const ext=path.extname(out);
  for(let c0=0;c0<N;c0+=CH){const c1=Math.min(N,c0+CH);let i=0;
   for(let f=c0;f<c1;f++){for(let k=0;k<K;k++){const t=Math.max(0,f/FPS+(k-1.5)*sub);await p.evaluate(t=>seek(t),t);
     await p.screenshot({path:path.join(tmp,String(i++).padStart(6,'0')+'.png'),omitBackground:info.alpha});}}
   const seg=path.join(tmp,'seg'+String(segs.length).padStart(4,'0')+ext);
   const want=c1-c0;   // force exactly `want` frames per chunk (clone the last if ffmpeg dropped any) so timing can't drift across chunks
   execFileSync('ffmpeg',['-loglevel','error','-y','-framerate',fr[1],'-i',path.join(tmp,'%06d.png'),'-vf',vf+`,tpad=stop_mode=clone:stop=${want},trim=end_frame=${want}`,'-r',fr[0],...enc.filter(x=>x!=='+faststart'&&x!=='-movflags'),seg]);
   const got=+execFileSync('ffprobe',['-v','error','-count_packets','-select_streams','v','-show_entries','stream=nb_read_packets','-of','csv=p=0',seg]).toString().trim();
   if(got!==want) process.stderr.write(`WARN chunk ${segs.length+1}: ${got}/${want} frames\n`);
   for(const f of fs.readdirSync(tmp)) if(f.endsWith('.png')) fs.unlinkSync(path.join(tmp,f));
   segs.push(seg); process.stderr.write(`chunk ${segs.length}/${Math.ceil(N/CH)}\n`);}
  fs.writeFileSync(path.join(tmp,'list.txt'),segs.map(s=>`file '${s}'`).join('\n'));
  execFileSync('ffmpeg',['-loglevel','error','-y','-f','concat','-safe','0','-i',path.join(tmp,'list.txt'),'-c','copy',...(info.alpha?[]:['-movflags','+faststart']),out]);
  fs.rmSync(tmp,{recursive:true,force:true});await b.close();
 } else {
 const ff=spawn('ffmpeg',['-loglevel','error','-y','-f','image2pipe','-framerate',fr[1],'-c:v','png','-i','-','-vf',vf,'-r',fr[0],...enc,out]);
 ff.stderr.on('data',d=>process.stderr.write(d));
 for(let f=0;f<N;f++){for(let k=0;k<K;k++){const t=Math.max(0,f/FPS+(k-1.5)*sub);await p.evaluate(t=>seek(t),t);
   const buf=await p.screenshot({type:'png',omitBackground:info.alpha});
   if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));}}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
 }
 console.log('rendered',out,N,'frames',errs.length?'ERR '+errs[0]:'');
})();
