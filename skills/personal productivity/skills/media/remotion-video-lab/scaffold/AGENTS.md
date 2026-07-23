# AGENTS.md — Remotion Video LAB

Any AI tool working in this folder: this is a **Remotion + ffmpeg** workspace for
turning raw screen recordings into focused, captioned, scored demo videos.

## Golden rule
NEVER cut before the user confirms. 1) read raw clip → 2) propose segment agenda
→ 3) confirm → 4) edit. Captions default to the user's language.

## Per-project layout
```
public/<name>/source.mp4      raw clip (+ optional music.mp3)
projects/<name>/project.json  config: id, fps, width/height, overlap, segments, captions, blurs
projects/<name>/out/          renders + review/ thumbnails
src/EditedVideo.tsx           prop-driven composition; src/projects.ts = registry
scripts/*.mjs                 ffmpeg pipeline (each takes <name>)
```

## New project
1. `mkdir -p public/<name> projects/<name>/out` ; copy clip to `public/<name>/source.mp4`
2. copy `projects/sample/project.json`; set id/fps/size; register import in `src/projects.ts`
3. `npm run dev` to preview; `npx remotion render <Id> projects/<name>/out/final.mp4`

## Pipeline (each takes a project name)
- `npm run keepRanges -- <name>` + `npm run cut -- <name>` : auto-drop frozen parts
- `npm run music -- <name> <sec>` / `npm run narrate -- <name>` (macOS) / `npm run mix -- <name>`
- `npm run blur -- <name>` : ffmpeg post-blur regions (CSS blur on video is ignored by renderer)
- frame grabs: use `node_modules/ffmpeg-static/ffmpeg` (no ffprobe dependency; mediaInfo reads ffmpeg banner)

fps 30, musicVolume ~0.15, overlap 12, dims = half source rounded even, target 60–90s.
