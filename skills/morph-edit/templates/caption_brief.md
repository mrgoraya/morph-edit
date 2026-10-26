# Caption translation brief (one subagent per chunk, run 4 in parallel)

Replace {N}, {VIDEO CONTEXT}, {LANGUAGE} and {SCRIPT} before sending. Extend the glossary for the video.

---
You are preparing YouTube caption cues for a video in {LANGUAGE} (it may mix in English words).

INPUT: motion/work/cap/chunk{N}.json: a list of {"i","s","e","orig"}. "orig" is a raw Whisper transcript, with mishearings.
OUTPUT: write motion/work/cap/out{N}.json with EXACTLY one {"i","orig","en"} per input cue, same order and ids. "orig" is the cleaned text in {SCRIPT}; "en" is the English subtitle. Reply only with the count and any unsure cues (id and why), max 10 lines.

VIDEO CONTEXT: {2-5 sentences: what the creator shows, product names, file names, settings}

GLOSSARY (fix mishearings): {wrong -> right, one per line: product names, people, technical terms}

RULES:
- "orig": fix mishearings and spelling, keep the speaker's words. Do not paraphrase.
- "en": natural, concise subtitle meaning, exact product and file names, no added facts. Fragments should read smoothly across consecutive cues.
- Do not merge, split, drop or reorder cues. For a garbled cue give the best faithful reading from context.
---
