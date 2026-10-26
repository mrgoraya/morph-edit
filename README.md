# morph-edit

Give Claude Code a talking-head video and it makes motion-graphic B-roll timed to your words. Every clip is **one shape that never cuts**: it morphs its size, corners and colour while its content swaps with a short blur, and a cursor drives each change with a real click or drag.

You get:
- the clips, ready to drop into your editor
- a preview of your video with the clips cut in
- `TIMING.md` (where each clip goes and what it covers)
- an HTML page with every clip, a step-through viewer, and a before/after compare page

## About

Free skill for Claude Code that turns a talking-head video into motion-graphic B-roll timed to your words, with optional sound effects, subscribe cards and captions. It runs on your own computer with no API costs, and you finish the edit in your own video editor.

## Skills

| Skill | What it does |
|---|---|
| `morph-edit` | Give it a video and it makes motion-graphic B-roll timed to your words, plus optional UI sound effects, subscribe cards and English + original-language captions. |

## What it does (and doesn't)

- **Motion-graphic B-roll clips** timed to your words, plus a preview with the clips cut in.
- **UI sound effects** (clicks, pops, whooshes) synthesised on your computer and timed to each clip's animation. They are muxed into the clips and mixed under your voice in the preview.
- **Subscribe cards** (an end card and short reminders) as clips, with your channel name, handle and logo.
- **Captions** as two SRT files, one in the spoken language and one in English, to upload as closed captions.

It does not cut your video, make thumbnails or write the title. You drop the clips into your own editor (Premiere, DaVinci, CapCut, Final Cut).

## Install and use with Claude Code

You need [Claude Code](https://claude.com/claude-code) installed first. Then follow these steps in order.

### Step 1: Open Claude Code in your video folder

Open a terminal (on Windows, open **Ubuntu** after installing WSL: run `wsl --install` in PowerShell, restart, then open Ubuntu), go to the folder with your video, and start Claude Code:

```bash
cd path/to/your/video-folder
claude
```

Everything below happens inside Claude Code.

### Step 2: Install the tools it needs

morph-edit needs **Node 18+**, **Python 3** and **ffmpeg** (with the `prores_ks` encoder). Pick one:

**Easiest: let Claude do it.** Paste this into Claude Code:

> Check my operating system and which of Node 18+, Python 3 and ffmpeg (with the `prores_ks` encoder) are already installed. Tell me what's missing, then install only those, using Homebrew on macOS or apt in Ubuntu/WSL, and ask me before each install.

Claude can't type your admin password. If an install asks for it, enter it yourself.

**Or install them yourself:**
- Mac: `brew install node ffmpeg python`
- Ubuntu / WSL: `sudo apt install nodejs npm ffmpeg python3 python3-venv python3-pip`

Native Windows (PowerShell) is untested, so use WSL.

### Step 3: Install morph-edit

Type these two commands in Claude Code:

```
/plugin marketplace add mrgoraya/morph-edit
/plugin install morph-edit@morph-edit
```

Restart Claude Code if it asks you to.

*No plugin?* Paste this instead:

> Download https://github.com/mrgoraya/morph-edit and copy its `skills/morph-edit` folder into this project's `.claude/skills/` folder. Then tell me when it is ready.

### Step 4: Make your B-roll

Paste this (change the file name):

> Use the morph-edit skill on `my-video.mp4`. Set it up if this is the first run, transcribe the video, and show me the transcript so I can fix any names. Then give me the clip plan table and wait for my approval before building anything.

The first run also installs Playwright, Chromium and Whisper. That takes a few minutes.

### Step 5: Answer a few questions and approve the plan

Claude asks how many clips you want and for your brand colours or logo. It shows the clip plan table, and nothing is built until you approve it.

### Step 6: Get your results in the `motion/out/` folder:
- the clips (`.mp4`, plus transparent `.mov` panels) and `sfx/` (the sound effects as WAV files)
- `captions/` (if you asked for captions)
- `TIMING.md`: where each clip goes and what it covers
- `preview.mp4`: your video with the clips cut in
- `index.html`, `viewer.html`, `compare.html`: open `index.html` first

The preview is for review. For the final video, place the clips in your own editor.

Tips: if you already have a transcript (`.srt`), put it in the folder and say so. It works with mixed-language speech (for example Urdu and English). Say "light", "medium" or "heavy" to choose how many clips you get. Add "with sound effects", "with a subscribe card" or "with captions" to the prompt to get those too.

## Credits

morph-edit is built on **[motion-graphics](https://github.com/Barty-Bart/motion-graphics)** by Bart Slodyczka ([@Barty-Bart](https://github.com/Barty-Bart)), MIT licensed. His `motion-broll` skill is the engine this project grew from: the clip engine, renderer, example clips and style. Please check out his repo and his other free skills. This project is not affiliated with or endorsed by him.

Additions in this repo by Mehran Rasheed: local Whisper transcription (`transcribe.py`, works with mixed-language speech), UI sound effects synthesised locally (`sfx.py`, no samples), subscribe card templates, caption tools (`scripts/captions/`), the one-page clip gallery (`make_gallery.py`), a preview height option in `composite.py`, previews of transparent panels over their own footage, 4K stills, and setup fixes.

Also included:
- Geist and Geist Mono fonts, SIL Open Font License 1.1 (`skills/morph-edit/engine/fonts/OFL-Geist.txt`)
- Icon paths adapted from Lucide, ISC License

## License

MIT. See `LICENSE`. Bart Slodyczka's copyright notice is kept as the license requires.
