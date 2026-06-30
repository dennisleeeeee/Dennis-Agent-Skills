// Cut and concatenate a project's keep-ranges into <project>/out/edited.mp4 using ffmpeg.
// Usage: node scripts/cutWithFfmpeg.mjs <project-name>
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, rmSync, statSync } from "node:fs";
import { resolve } from "node:path";
import { loadProject, FFMPEG } from "./lib/project.mjs";

const project = loadProject();
const data = JSON.parse(readFileSync(project.keepRanges, "utf8"));
const SRC = project.source;

const tmp = project.out("_segments");
rmSync(tmp, { recursive: true, force: true });
mkdirSync(tmp, { recursive: true });

const parts = [];
data.ranges.forEach((r, i) => {
  const file = `${tmp}/part_${String(i).padStart(3, "0")}.mp4`;
  const dur = (r.endSec - r.startSec).toFixed(3);
  console.log(`[${i + 1}/${data.ranges.length}] ${r.startSec}s -> ${r.endSec}s  (${dur}s)`);
  execFileSync(
    FFMPEG,
    [
      "-y", "-hide_banner", "-loglevel", "error",
      "-ss", String(r.startSec), "-i", SRC, "-t", dur,
      "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
      "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", file,
    ],
    { stdio: "inherit" },
  );
  parts.push(file);
});

const listFile = `${tmp}/list.txt`;
writeFileSync(listFile, parts.map((p) => `file '${resolve(p)}'`).join("\n"));

const out = project.out("edited.mp4");
console.log(`\nConcatenating -> ${out}`);
execFileSync(
  FFMPEG,
  ["-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listFile, "-c", "copy", out],
  { stdio: "inherit" },
);

const sizeMB = (statSync(out).size / 1024 / 1024).toFixed(2);
console.log(`Done: ${out}  (${sizeMB} MB, ~${data.totalKeptSec}s)`);
