# Remotion Video LAB — reference & gotchas

## Privacy blur
- To hide sensitive on-screen text define `blurs` in project.json (`seg, atSec, durSec, x, y, w, h` in composition px == final.mp4 px) then `npm run blur -- <name>`.
- Post-processes out/final.mp4, keeps clean backup final-noblur.mp4, idempotent.
- DO NOT use CSS blur in Remotion: backdrop-filter/filter on OffthreadVideo/Video are IGNORED (video composited server-side). ffmpeg boxblur is the only reliable way.
- boxblur chroma radius max 7 (yuv420) → pass luma:power:chroma:power e.g. boxblur=10:3:5:3. Measure box coords from output stills with drawgrid; content sits further left than it looks.

## Pipeline gotchas
- No runnable ffprobe on some Macs (x86, no Rosetta) → mediaInfo() reads ffmpeg banner. Never reintroduce ffprobe. Use node_modules/ffmpeg-static/ffmpeg for frame grabs.
- musicFile must be a real path before `npm run music` (empty string → ffmpeg fails).
- src/projects.ts can be clobbered when multiple videos built in parallel. Symptom: "Could not find composition ID X" with yours missing → re-add import + array entry. "No target found for targetId" puppeteer warning is harmless.
- npm scripts take a project name: keepRanges/cut/music/narrate/mix/blur -- <name>.

## Zoom (readable typing / code)
- Per-segment optional fields in project.json: `zoom` (scale >1), `zoomX`/`zoomY` (focal point 0..1), `zoomInSec` (smooth ramp). Rendered via CSS transform on the video wrapper — Remotion honors transform/scale (unlike CSS blur, which is ignored). Use for typing/coding shots: pair with `rate` ≤ 1.0 so text is slow AND large.

## Workflow
- read raw clip → propose agenda → confirm with user → then cut. fps30, bgm0.15, 7-seg structure, dims = half source rounded even.
- tech demo: read raw → design 字幕腳本 → propose edit plan + time allocation → user approves → edit. Typing actions = slow (rate≤1) + zoom in.
