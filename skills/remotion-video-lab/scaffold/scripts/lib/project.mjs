// Shared helpers so every pipeline script works on a named project folder.
//
// A project lives in projects/<name>/ and owns its own config, intermediate
// files and final renders. This lets many unrelated videos coexist in one repo
// without overwriting each other.
//
//   projects/<name>/project.json   <- config (segments, fps, size, assets)
//   projects/<name>/keepRanges.json
//   projects/<name>/subtitles.ass
//   projects/<name>/out/           <- all generated files for this project
//
// Source video / music live under public/ (so Remotion's staticFile() can read
// them) at the paths named in project.json (sourceFile / musicFile).
import { readFileSync, mkdirSync } from "node:fs";
import { resolve, join } from "node:path";
import { spawnSync } from "node:child_process";
import ffmpegStatic from "ffmpeg-static";

export const FFMPEG = ffmpegStatic;

// This repo only ships an arm64 ffmpeg-static and there may be no runnable
// ffprobe on the machine (the bundled / system ffprobe can be x86 with no
// Rosetta). So we read media info straight from ffmpeg's banner instead of
// depending on ffprobe at all.

// Parse "Duration: HH:MM:SS.ss" and the video stream's fps from ffmpeg stderr.
export function mediaInfo(path) {
  const r = spawnSync(FFMPEG, ["-hide_banner", "-i", path], { encoding: "utf8" });
  const text = `${r.stderr || ""}`;

  let duration = NaN;
  const d = text.match(/Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)/);
  if (d) duration = Number(d[1]) * 3600 + Number(d[2]) * 60 + Number(d[3]);

  let fps = NaN;
  const f = text.match(/(\d+(?:\.\d+)?)\s*fps/);
  if (f) fps = Number(f[1]);

  if (Number.isNaN(duration)) {
    console.error(`Could not read duration from ffmpeg for: ${path}`);
    process.exit(1);
  }
  return { duration, fps };
}

export const mediaDuration = (path) => mediaInfo(path).duration;



// Read the project name from argv (or env), printing usage on failure.
export function projectName() {
  const name = process.argv[2] || process.env.PROJECT;
  if (!name) {
    const script = process.argv[1]?.split("/").pop() || "<script>.mjs";
    console.error(`Usage: node scripts/${script} <project-name>`);
    console.error("   or: PROJECT=<project-name> node scripts/" + script);
    process.exit(1);
  }
  return name;
}

// Resolve every path a project script might need.
export function loadProject(name = projectName()) {
  const dir = resolve("projects", name);
  let config;
  try {
    config = JSON.parse(readFileSync(join(dir, "project.json"), "utf8"));
  } catch {
    console.error(`Cannot read projects/${name}/project.json — does the project exist?`);
    process.exit(1);
  }
  const outDir = join(dir, "out");
  mkdirSync(outDir, { recursive: true });

  return {
    name,
    dir,
    config,
    source: resolve("public", config.sourceFile),
    music: resolve("public", config.musicFile),
    keepRanges: join(dir, "keepRanges.json"),
    subtitles: join(dir, "subtitles.ass"),
    outDir,
    // Path to a file inside this project's out/ folder.
    out: (rel) => join(outDir, rel),
  };
}
