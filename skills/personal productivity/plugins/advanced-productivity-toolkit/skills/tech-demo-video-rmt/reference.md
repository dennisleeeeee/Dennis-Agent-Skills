# Quick Video Edit — reference & gotchas

Standalone reference. The skill stores only custom logic (`scaffold/src/` +
`scaffold/scripts/`); the Remotion project skeleton, configs and `node_modules`
are generated on the user's machine at bootstrap. No dependency on any other skill.

## Bootstrap (regenerate the skeleton on the user's machine)
- `npx create-video --yes --blank --no-tailwind <SCRATCH>` scaffolds a blank
  Remotion project and installs deps. Must NOT run inside a git repo.
- Overlay `scaffold/src/*` and `scaffold/scripts/*` into `<SCRATCH>` (overwrites
  the generated `src/Root.tsx` and `src/index.ts`).
- `npm install --save-dev ffmpeg-static`, then register the pipeline scripts:
  `keepRanges/cut/music/narrate/mix/blur` → `node scripts/<file>.mjs`.

## Environment gotchas (verified in the field)
- **`npm min-release-age` / `before` supply-chain lock**: some machines pin npm to
  packages older than N days. `create-video` installs the newest Remotion, but a
  later `npm install` under the lock can't resolve it and CORRUPTS `node_modules`
  (symptom: `@remotion/cli` listed in deps but missing, `ETARGET notarget ... with
  a date before <date>`). Fix: run every install with `--min-release-age=0` (do
  NOT combine with `--before`). If already broken: `npm install --min-release-age=0`.
- **`npx remotion` may fail** with "could not determine executable to run". Call the
  project-local bin instead: `node_modules/.bin/remotion render <Id> out.mp4`
  (Windows PowerShell: `& "$PROJ\node_modules\.bin\remotion.cmd" render ...`).
- **Reading the clip before the heavy install**: to grab frames for the agenda you
  only need ffmpeg — `npm i ffmpeg-static` in a tiny scratch dir is enough; defer
  the full `create-video` until the plan is approved.

## project.json schema (write one per clip; no sample is shipped)
```json
{
  "id": "MyDemo",               // unique composition id (used by remotion render)
  "title": "My demo edit",
  "fps": 30,
  "width": 1280,                 // half source width, even number
  "height": 720,                 // half source height, even number
  "overlap": 12,                 // crossfade frames between segments
  "sourceFile": "mydemo/source.mp4",   // path under public/
  "musicFile": "mydemo/music.mp3",     // optional; omit if no bgm
  "musicVolume": 0.15,
  "segments": [
    { "name": "Intro", "srcStart": 0, "srcEnd": 10, "rate": 1.2 },
    { "name": "Typing", "srcStart": 12, "srcEnd": 22, "rate": 0.8, "zoom": 1.6, "zoomX": 0.35, "zoomY": 0.55, "zoomInSec": 0.8 },
    { "name": "Key reveal", "srcStart": 30, "srcEnd": 45, "rate": 1.0 }
  ],
  "captions": [
    { "seg": 0, "atSec": 0.5, "durSec": 4, "text": "標題", "sub": "副標" }
  ],
  "blurs": []                    // optional privacy blur regions
}
```
Register it in `src/projects.ts`: `import myclip from "../projects/myclip/project.json";`
and add `myclip` to `PROJECT_CONFIGS`.

## Zoom (readable typing / code)
- Per-segment optional fields in `project.json`: `zoom` (scale >1), `zoomX`/`zoomY`
  (focal point 0..1), `zoomInSec` (smooth ramp-in), `zoomOutSec` (smooth ramp-out
  at the segment's end so it eases back to 1.0 — feels less static than holding).
  Rendered via CSS transform on the video wrapper (eased in→hold→out) — Remotion
  honors transform/scale (unlike CSS blur, which is ignored). Use for typing/coding
  shots: pair with `rate` ≤ 1.0 so text is slow AND large. Example segment:
  `{ "name": "Typing", "srcStart": 12, "srcEnd": 22, "rate": 0.8, "zoom": 1.2, "zoomX": 0.72, "zoomY": 0.3, "zoomInSec": 0.6, "zoomOutSec": 0.6 }`.
- Keep `zoom` modest (≈1.2) for split-screen UIs (e.g. a chat panel on the right):
  a large zoom pushes edge content off-frame and looks lopsided. Aim the focal
  point at the content column, not the empty half.

## Privacy blur
- Define `blurs` in `project.json` (`seg, atSec, durSec, x, y, w, h` in composition
  px == final.mp4 px) then `npm run blur -- <name>`.
- Post-processes `out/final.mp4`, keeps a clean backup `final-noblur.mp4`, idempotent.
- DO NOT use CSS blur in Remotion: `backdrop-filter`/`filter` on OffthreadVideo/Video
  are IGNORED (video composited server-side). ffmpeg boxblur is the only reliable way.
- boxblur chroma radius max 7 (yuv420) → pass luma:power:chroma:power e.g.
  `boxblur=10:3:5:3`. Measure box coords from output stills with drawgrid.

## Pipeline gotchas
- No runnable `ffprobe` on some machines → `mediaInfo()` reads the ffmpeg banner.
  Never reintroduce ffprobe. Use `node_modules/ffmpeg-static/ffmpeg` for frame grabs.
- `musicFile` must be a real path before `npm run music` (empty string → ffmpeg fails).
- `src/projects.ts` must import each `project.json` and add it to `PROJECT_CONFIGS`;
  "Could not find composition ID X" means it isn't registered.
- npm scripts take a project name: `keepRanges/cut/music/narrate/mix/blur -- <name>`.
- `npm run narrate` uses macOS `say`; skip on other OSes.

## Workflow (tech demo)
read raw clip → design 字幕腳本 → propose edit plan + explicit time allocation →
user approves → edit. Typing/coding actions = slow (`rate` ≤ 1) + zoom in.
fps 30, bgm ~0.15, dims = half source rounded even.

## Cleanup (use & throw)
Everything runs in a disposable `SCRATCH` dir. After the final `.mp4` is exported
and the user confirms, delete the whole `SCRATCH`. Only the final video survives.
