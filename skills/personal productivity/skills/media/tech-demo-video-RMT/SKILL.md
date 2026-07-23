---
name: tech-demo-video-RMT
description: Self-contained, use-and-throw pipeline for editing TECH DEMO / product screen-recording videos with Remotion (RMT) — no persistent project to set up or maintain. Reads the raw clip first, designs a caption script (字幕腳本), proposes an edit plan with time allocation for the user to approve, and only then edits (trim dead time, speed up, captions, music, blur; slows down and zooms into typing/coding actions so the audience can read them). Built on Remotion + ffmpeg; the project skeleton is regenerated on the user's machine via `npx create-video` at bootstrap (the skill only stores its custom composition + ffmpeg scripts) so more effects can be added. Auto-bootstraps a throwaway scratch workspace and, after an explicit double-check, DELETES all generated code/intermediates keeping ONLY the final .mp4. Use for: "edit this tech demo", "剪這支 demo 影片", "產品示範影片剪輯", "quick video edit", "剪完幫我清掉 code", "不要留 project".
---

# Tech Demo Video (RMT) — tech-demo editing, ephemeral (use & throw)

A lightweight, **self-contained, session-scoped** way to turn a raw **tech demo /
product screen-recording** into a focused, captioned final video with Remotion —
without the user ever setting up or maintaining a project. The skill stores only
its custom logic under `scaffold/`; the Remotion project skeleton is regenerated
on the user's machine at bootstrap, so it works on any device — but the
whole workspace is treated as disposable: read → plan → approve → edit → export
final `.mp4` → **delete all the code**.

## What this skill is

A one-off editor: the user drops a raw clip, you edit it, and you leave behind
**only the final video** — no project, no `node_modules`, no scripts. The skill
stores **only its custom logic** under `scaffold/` (the Remotion composition in
`src/` and the ffmpeg pipeline in `scripts/`). Everything regenerable — the
Remotion project boilerplate, configs, and `node_modules` — is generated fresh on
the user's machine at bootstrap via `npx create-video`, so the skill stays tiny
and always uses a current, known-good project skeleton. ffmpeg itself comes from
`ffmpeg-static` via npm, so no system ffmpeg is required.

## Golden rule: read → script → plan → approve → edit

**NEVER start cutting before the user approves the plan.** For a tech demo the
order is strict:
1. **Read the raw clip fully first** — contact sheet + key full-res frames. Note
   the story, which features/UI are shown, and every **typing / coding action**
   (see the zoom rule below).
2. **Design the caption script (字幕腳本)** — write the actual on-screen caption
   lines segment by segment (in the user's language, default zh-TW), matched to
   what each moment demonstrates. This is a concrete script the user can review,
   not just a description.
3. **Propose the edit plan + time allocation** — a segment table: source
   timestamps → target duration, suggested speed/trim, what to emphasize, dead
   time to drop, and total runtime. Make the **time allocation explicit** (how
   many seconds each segment gets) so the user can rebalance.
4. **Ask the user to approve.** Even if they say "just do it", show the caption
   script + plan first and wait for explicit approval.
5. **Only then edit.**

## Typing / coding actions: slow down + zoom in

Whenever the raw clip contains someone **typing, editing code, or entering
input**, the audience must be able to read it clearly:
- **Slow it down**: for a typing segment use `rate` ≤ 1.0 (do NOT speed it up like
  dead time). Slow further (e.g. 0.6–0.8) if the text appears too fast to follow.
- **Zoom in**: scale up / crop to the code editor or input area so the characters
  are large and legible, ideally with a smooth zoom into the region of interest.
- These are per-segment fields in `project.json` (supported by the shared
  composition): `zoom` (target scale, e.g. 1.2), `zoomX`/`zoomY` (focal point
  0..1 aimed at the editor/input), `zoomInSec` (smooth ramp-in) and `zoomOutSec`
  (smooth ramp-out so it eases back out at the end — smoother than holding). A
  typing segment therefore looks like
  `{ "name": "Typing", "srcStart": .., "srcEnd": .., "rate": 0.8, "zoom": 1.2, "zoomX": 0.72, "zoomY": 0.3, "zoomInSec": 0.6, "zoomOutSec": 0.6 }`.
  Keep `zoom` modest (~1.2) on split-screen UIs so edge content isn't cropped.
- Call these out explicitly in the edit plan (mark segments as "typing → slow +
  zoom") so the user sees them during approval.
- Hold on the final typed result a beat longer before moving on.

## Phases

### 0. Agree on the final output path (before any work)
Ask where the finished video should land. Default: next to the source as
`<sourceName>_edited.mp4`. This is the ONLY file that survives cleanup, so pin it
down early. Record it as `FINAL_OUT`.

### 1. Bootstrap a throwaway scratch workspace
Generate a fresh Remotion project on the user's machine, then overlay this skill's
custom files. Record the scratch path as `SCRATCH` — you will delete this whole
directory later, so keep it precise. Do this OUTSIDE any git repo (create-video
refuses to run inside one) and NOT inside the user's important folders.

```bash
SKILL_DIR="<this-skill-dir>"
SCRATCH="${TMPDIR:-/tmp}/qve-$(date +%s)"

# 1. Scaffold a blank Remotion project (installs node_modules). Non-interactive.
npx create-video --yes --blank --no-tailwind "$SCRATCH"

# 2. Overlay the skill's custom composition + ffmpeg scripts (overwrites the
#    generated src/Root.tsx and src/index.ts on purpose).
cp -R "$SKILL_DIR/scaffold/src/."     "$SCRATCH/src/"
cp -R "$SKILL_DIR/scaffold/scripts/." "$SCRATCH/scripts/"

# 3. Add ffmpeg + register the pipeline npm scripts (see reference.md).
cd "$SCRATCH"
npm install --save-dev ffmpeg-static
npm pkg set scripts.keepRanges="node scripts/computeKeepRanges.mjs" \
            scripts.cut="node scripts/cutWithFfmpeg.mjs" \
            scripts.music="node scripts/makeMusic.mjs" \
            scripts.narrate="node scripts/makeNarration.mjs" \
            scripts.mix="node scripts/mixFinal.mjs" \
            scripts.blur="node scripts/blurRegions.mjs"
```
Windows (PowerShell): set `$SCRATCH = Join-Path $env:TEMP "qve-$(Get-Date -Format yyyyMMddHHmmss)"`,
run the same `npx create-video --yes --blank --no-tailwind $SCRATCH`, then use
`Copy-Item -Recurse -Force` to overlay `scaffold\src\*` and `scaffold\scripts\*`,
and the same `npm install` / `npm pkg set` commands. ffmpeg comes from
`ffmpeg-static` — no system ffmpeg needed.

Then create one project inside the scratch: `mkdir -p public/<name> projects/<name>/out`,
copy the raw clip to `public/<name>/source.mp4`, write `projects/<name>/project.json`
(schema in `reference.md`: set `id`, `sourceFile`, `fps` 30, `width`/`height` =
half source dims rounded even, `segments`, `captions`), and register it in
`src/projects.ts` (import the project.json and add it to `PROJECT_CONFIGS`).

### 2. Read the clip, write the caption script & edit plan
Grab frames with the bundled binary `node_modules/ffmpeg-static/ffmpeg` (contact
sheet + key stills). Then, following the Golden rule above:
- write the **caption script (字幕腳本)** line by line,
- build the **edit-plan table with explicit time allocation** per segment,
- flag every **typing/coding segment** as "slow + zoom in",
- present both to the user and **wait for approval** before editing.

### 3. Edit — and iterate
Cut segments, add captions from the approved script, apply slow+zoom on typing
segments, add music/narration, blur, and any extra effects. Because it's real
Remotion, the user can keep asking for adjustments:
- Re-render after each change: `npx remotion render <Id> projects/<name>/out/final.mp4`.
- Show the user a still/preview and ask if it's good.
- Loop until they're satisfied. Nothing is deleted during this phase.

### 4. Export the final MP4
Copy the confirmed render to `FINAL_OUT` (outside the scratch dir):
```bash
cp "$SCRATCH/projects/<name>/out/final.mp4" "$FINAL_OUT"
```
Verify `FINAL_OUT` exists and is playable before proceeding.

### 5. Double-check, THEN delete the code
- Confirm with the user explicitly: "最終影片已存到 `<FINAL_OUT>`,要我把暫存
  的 project / code 全部刪掉嗎?" (or English equivalent).
- Only after an explicit YES, delete the entire scratch workspace:
```bash
rm -rf "$SCRATCH"     # Windows: Remove-Item -Recurse -Force $SCRATCH
```
- Report what remains: only `FINAL_OUT`. Everything else (node_modules, src,
  scripts, projects, intermediate renders) is gone.

## Cleanup safety (important)
- Delete **only** the `SCRATCH` directory this skill created. Never `rm -rf` the
  user's source folder, home dir, or anything you didn't create.
- Keep the raw source file untouched; copy it into scratch, don't move it.
- Never delete before `FINAL_OUT` is verified to exist and the user has confirmed.
- If the user asks to keep the code after all, skip step 5 and just report the
  scratch path so they can keep working in it.
- If any render/export step failed, do NOT clean up — leave scratch intact so the
  work can be recovered.

## Conventions
fps 30, dims = half source rounded even, ~60–90s pacing, bgm ~0.15, crossfade
`overlap` ≈ 12 frames, lower-third captions. Run `npx tsc` after editing
`src/*`. See `reference.md` for the bootstrap steps, `project.json` schema, zoom,
blur math, and pipeline gotchas.
