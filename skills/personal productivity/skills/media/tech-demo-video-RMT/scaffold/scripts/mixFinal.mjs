// Mix a project's edited video + narration + bgm + burned-in subtitles -> out/edited_final.mp4.
// Usage: node scripts/mixFinal.mjs <project-name>
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { loadProject, FFMPEG } from "./lib/project.mjs";

const project = loadProject();
const cues = JSON.parse(readFileSync(project.out("tts/cues.json"), "utf8"));

const edited = project.out("edited.mp4");
const bgm = project.music;
const subtitles = project.subtitles;
const finalOut = project.out("edited_final.mp4");

const inputs = ["-i", edited, "-i", bgm];
for (const c of cues) inputs.push("-i", c.wav);

const parts = [];
parts.push(`[0:v]subtitles=${subtitles}[v]`);
const narrLabels = [];
cues.forEach((c, i) => {
  const ms = Math.round(c.start * 1000);
  const inIdx = 2 + i;
  parts.push(`[${inIdx}:a]adelay=${ms}|${ms},volume=1.6[n${i}]`);
  narrLabels.push(`[n${i}]`);
});
parts.push(`${narrLabels.join("")}amix=inputs=${narrLabels.length}:normalize=0:dropout_transition=0[narr]`);
parts.push(`[1:a]volume=0.09,afade=t=in:st=0:d=2,afade=t=out:st=110:d=2.4[bg]`);
parts.push(`[narr][bg]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[aout]`);

const filter = parts.join(";");

const args = [
  "-y",
  ...inputs,
  "-filter_complex", filter,
  "-map", "[v]", "-map", "[aout]",
  "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
  "-c:a", "aac", "-b:a", "192k",
  "-shortest",
  finalOut,
];

console.log("Running ffmpeg with", inputs.length / 2, "inputs");
execFileSync(FFMPEG, args, { stdio: "inherit" });
console.log(`Done: ${finalOut}`);
