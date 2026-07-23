// Parses ffmpeg freezedetect output and emits keep ranges (seconds) for a project's source video.
// Usage: node scripts/computeKeepRanges.mjs <project-name>
import { spawnSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { loadProject, FFMPEG, mediaInfo } from "./lib/project.mjs";

const project = loadProject();
const SRC = project.source;

const FREEZE_NOISE = 0.003; // pixel diff threshold
const FREEZE_MIN_DUR = 5.0; // seconds to qualify as "boring"
const MERGE_GAP = 1.0;      // merge skips closer than this
const MIN_KEEP = 1.0;       // drop kept slivers shorter than this
const HEAD_TRIM = 0.1;      // trim a bit off each kept range edge
const TAIL_TRIM = 0.1;

const info = mediaInfo(SRC);
const duration = info.duration;
const fps = info.fps;

const log = spawnSync(
  FFMPEG,
  [
    "-hide_banner", "-nostats",
    "-i", SRC,
    "-vf", `freezedetect=n=${FREEZE_NOISE}:d=${FREEZE_MIN_DUR}`,
    "-map", "0:v", "-f", "null", "-",
  ],
  { maxBuffer: 64 * 1024 * 1024, encoding: "utf8" },
).stderr;

const skips = [];
let curStart = null;
for (const line of log.split("\n")) {
  const s = line.match(/freeze_start: ([\d.]+)/);
  const e = line.match(/freeze_end: ([\d.]+)/);
  if (s) curStart = parseFloat(s[1]);
  if (e && curStart != null) {
    skips.push([curStart, parseFloat(e[1])]);
    curStart = null;
  }
}
if (curStart != null) skips.push([curStart, duration]);

// Merge close skips
skips.sort((a, b) => a[0] - b[0]);
const merged = [];
for (const [s, e] of skips) {
  if (merged.length && s - merged[merged.length - 1][1] <= MERGE_GAP) {
    merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], e);
  } else {
    merged.push([s, e]);
  }
}

// Invert -> keep ranges
const keep = [];
let cursor = 0;
for (const [s, e] of merged) {
  if (s > cursor) keep.push([cursor, s]);
  cursor = Math.max(cursor, e);
}
if (cursor < duration) keep.push([cursor, duration]);

// Trim & filter
const ranges = keep
  .map(([s, e]) => [s + HEAD_TRIM, e - TAIL_TRIM])
  .filter(([s, e]) => e - s >= MIN_KEEP)
  .map(([s, e]) => ({
    startSec: +s.toFixed(3),
    endSec: +e.toFixed(3),
    durationSec: +(e - s).toFixed(3),
  }));

const totalKept = ranges.reduce((a, r) => a + r.durationSec, 0);

const out = {
  source: project.config.sourceFile,
  fps,
  sourceDurationSec: +duration.toFixed(3),
  totalKeptSec: +totalKept.toFixed(3),
  totalKeptFrames: Math.round(totalKept * fps),
  ranges,
};

writeFileSync(project.keepRanges, JSON.stringify(out, null, 2));
console.log(
  `Wrote ${ranges.length} keep ranges -> ${project.keepRanges}\n` +
    `Original: ${duration.toFixed(1)}s, Kept: ${totalKept.toFixed(1)}s ` +
    `(${((totalKept / duration) * 100).toFixed(1)}%) @ ${fps}fps`,
);
