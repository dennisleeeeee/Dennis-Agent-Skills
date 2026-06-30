// Apply privacy region-blur to a project's rendered final.mp4 using ffmpeg.
//
// Remotion's OffthreadVideo is composited server-side, so CSS blur over the
// video does not work in-render. Instead we render clean and blur regions here
// as a deterministic post-process, driven by the same project.json "blurs".
//
// Each blur is anchored to a segment in OUTPUT time (atSec/durSec, like a
// caption) and a rectangle in composition px (== final.mp4 px). We compute the
// absolute time window from the segment layout, then chain crop+boxblur+overlay
// filters, each gated with enable='between(t,t0,t1)'.
//
//   npm run blur -- <project-name>
//
// Idempotent: the clean render is preserved as out/final-noblur.mp4 and every
// run blurs from that source into out/final.mp4.
import { spawnSync } from "node:child_process";
import { existsSync, renameSync, copyFileSync } from "node:fs";
import { FFMPEG, loadProject } from "./lib/project.mjs";

const { config, out } = loadProject();
const { fps, overlap, segments, blurs } = config;

if (!blurs || blurs.length === 0) {
  console.log("No blurs defined in project.json — nothing to do.");
  process.exit(0);
}

// Replicate the composition's segment layout (see EditedVideo.tsx).
const segLen = (s) => Math.max(1, Math.round(((s.srcEnd - s.srcStart) * fps) / s.rate));
const starts = [];
let acc = 0;
for (const s of segments) {
  starts.push(acc);
  acc += segLen(s) - overlap;
}

const regions = blurs.map((b) => {
  const startFrame = (starts[b.seg] ?? 0) + Math.round(b.atSec * fps);
  const t0 = startFrame / fps;
  const t1 = t0 + b.durSec;
  return { x: b.x, y: b.y, w: b.w, h: b.h, t0, t1 };
});

const noblur = out("final-noblur.mp4");
const final = out("final.mp4");

// Preserve the clean render once, then always blur from it.
if (!existsSync(noblur)) {
  if (!existsSync(final)) {
    console.error(`Missing ${final} — render the project first.`);
    process.exit(1);
  }
  renameSync(final, noblur);
}

// Build the filter graph: chain split -> crop+boxblur -> time-gated overlay.
const parts = [];
let prev = "0:v";
regions.forEach((r, i) => {
  const radius = Math.max(3, Math.min(10, Math.floor(Math.min(r.w, r.h) / 2) - 1));
  // Chroma planes are half-resolution in yuv420 (max boxblur radius 7).
  const chroma = Math.min(7, Math.max(1, Math.floor(radius / 2)));
  const base = `base${i}`;
  const src = `src${i}`;
  const bb = `bb${i}`;
  const outLbl = `v${i}`;
  parts.push(`[${prev}]split=2[${base}][${src}]`);
  parts.push(`[${src}]crop=${r.w}:${r.h}:${r.x}:${r.y},boxblur=${radius}:3:${chroma}:3[${bb}]`);
  parts.push(
    `[${base}][${bb}]overlay=${r.x}:${r.y}:enable='between(t,${r.t0.toFixed(3)},${r.t1.toFixed(3)})'[${outLbl}]`,
  );
  prev = outLbl;
});

const filter = parts.join(";");

console.log(`Blurring ${regions.length} region(s) -> ${final}`);
for (const r of regions) {
  console.log(`  [${r.t0.toFixed(2)}s..${r.t1.toFixed(2)}s]  ${r.w}x${r.h} @ (${r.x},${r.y})`);
}

const args = [
  "-y",
  "-hide_banner",
  "-loglevel",
  "error",
  "-stats",
  "-i",
  noblur,
  "-filter_complex",
  filter,
  "-map",
  `[${prev}]`,
  "-map",
  "0:a?",
  "-c:v",
  "libx264",
  "-crf",
  "18",
  "-preset",
  "medium",
  "-pix_fmt",
  "yuv420p",
  "-c:a",
  "copy",
  final,
];

const r = spawnSync(FFMPEG, args, { stdio: "inherit" });
if (r.status !== 0) {
  console.error("ffmpeg blur failed.");
  process.exit(r.status ?? 1);
}
console.log(`Done: ${final}`);
