---
name: remotion-video-lab
description: Portable, self-bootstrapping pipeline for editing screen-recording / demo videos ("毛片", raw clip) into focused, captioned, scored final cuts using Remotion + ffmpeg. Use when the user wants to turn a raw recording into a polished demo video — trimming dead time, speeding up slow parts, adding captions/subtitles, background music, narration, or privacy blur. Triggers: "剪輯", "優化剪輯", "edit this clip", "make a demo video", "加字幕", "加音樂", "去冷場", dropping a video path. This skill carries its own scaffold so it can recreate the whole workspace on any device. Enforces an agenda-first review-and-confirm workflow before cutting.
---

# Remotion Video LAB — portable demo-video editing

A consistent, repeatable, **device-independent** pipeline for turning a raw
screen recording into a focused, captioned, scored final video. The skill ships
the full workspace scaffold (`scaffold/`) so it can bootstrap from nothing on any
machine and any AI CLI.

## Golden rule: agenda first, then cut

**NEVER start cutting before the user confirms direction.** Phases, in order:
1. **Read the raw clip fully** — contact sheets + key full-res frames; read what
   is on screen (story, key UI, custom features).
2. **Propose the agenda** — segment-by-segment plan: source timestamps, what each
   shows, suggested speed/trim, story arc, what to emphasize, what dead time to drop.
3. **Discuss & confirm** — wait for explicit alignment.
4. **Only then edit.** If user says "just do it", still show the agenda first.
Default to writing captions in the user's language (zh-TW here).

## 0. Bootstrap the workspace (do this on a fresh device)

If there is no `package.json` with the `keepRanges/cut/music/blur` scripts, set up:
```bash
bash <skill-dir>/scaffold/setup.sh "<target-dir>"   # copies scaffold + npm install
```
This copies every file from `scaffold/` (scripts, src, configs) into the target,
then runs `npm install`. Dependencies: Node 18+, npm, and `ffmpeg-static` (arm64
+ x64 binaries are pulled by npm — no system ffmpeg/ffprobe needed). macOS `say`
is only required for `npm run narrate`. Manual alternative:
```bash
mkdir -p <target> && cp -R <skill-dir>/scaffold/. <target>/ && cd <target> && npm install
```

## Project layout (multi-project, isolated)

```
public/<name>/        source.mp4 + music.mp3 (served to Remotion preview)
projects/<name>/
  project.json        config: id, fps, size, overlap, segments, captions, blurs, assets
  keepRanges.json     auto-detected keep ranges (generated)
  subtitles.ass       narration cues (optional)
  out/                edited/final renders + review/ thumbnails
src/EditedVideo.tsx   generic prop-driven composition (segments + captions + blur types)
src/projects.ts       registry — import each project.json, add to EDITING_PROJECTS
scripts/*.mjs         ffmpeg pipeline, each takes a <project-name> arg
scripts/lib/project.mjs  resolves paths; mediaInfo() reads duration/fps from ffmpeg banner
```

## Media info portability (important)

No `ffprobe` dependency. `mediaInfo()` parses duration/fps from ffmpeg's banner,
so it works even where bundled/system ffprobe is the wrong arch. For ad-hoc frame
grabs always use the bundled binary: `node_modules/ffmpeg-static/ffmpeg`.

## Step-by-step

1. **Create project**: `mkdir -p public/<name> projects/<name>/out`; copy raw clip
   to `public/<name>/source.mp4`; copy an existing `project.json`; set `id`,
   `sourceFile`, `fps` (30), `width`/`height` (half source dims, even); register in `src/projects.ts`.
2. **Read clip for agenda** (don't skip): `FF=node_modules/ffmpeg-static/ffmpeg`;
   timeline scan `$FF -ss 0 -i public/<name>/source.mp4 -t 130 -vf "fps=1/10,scale=300:-1,tile=13x1" -frames:v 1 projects/<name>/out/review/scan.png`;
   key frames `$FF -ss 35 -i ... -frames:v 1 -q:v 3 out/review/f_35.png`. View, then propose agenda.
3. **Approach**: A) auto de-freeze `npm run keepRanges -- <name>` then `npm run cut -- <name>`;
   B) manual segments (preferred) — hand-pick `srcStart/srcEnd/rate` (rate>1 speeds up; key reveals ~1.0–1.2).
4. **Captions**: native Remotion overlay, anchored per segment. Add `captions` array; verify with `npx remotion still <Id> --frame=<f>`.
5. **Music/narration** (optional): `npm run music -- <name> <sec>`; `npm run narrate -- <name>` (macOS `say`); `npm run mix -- <name>`. Keep `musicVolume` ~0.12–0.18; `musicFile` must be a real path before `npm run music`.
6. **Render**: `npx remotion render <Id> projects/<name>/out/final.mp4`. Privacy blur via `blurs` + `npm run blur -- <name>` (ffmpeg post-process; CSS blur on Video is ignored by renderer).

## Conventions
- Caption: lower-third dark panel, blue left accent, bold main + smaller blue sub, CJK font stack, fade+slide.
- Pacing ~60–90s; drop dead time, breathe on key reveals; crossfade `overlap`≈12 frames.
- Run `npx tsc` after editing; keep `src/projects.ts` in sync.

See `reference.md` for blur math, gotchas, and per-project history.
