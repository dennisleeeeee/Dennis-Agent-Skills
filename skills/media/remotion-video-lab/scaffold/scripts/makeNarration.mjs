// Generate macOS `say` narration WAVs from a project's subtitles.ass.
// Usage: node scripts/makeNarration.mjs <project-name>
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join } from "node:path";
import { loadProject, FFMPEG, mediaDuration } from "./lib/project.mjs";

const project = loadProject();
const ASS = project.subtitles;
const OUT_DIR = project.out("tts");
mkdirSync(OUT_DIR, { recursive: true });

const text = readFileSync(ASS, "utf8");
const lines = text.split(/\r?\n/).filter((l) => l.startsWith("Dialogue:"));

const toSec = (t) => {
  const [h, m, s] = t.split(":");
  return Number(h) * 3600 + Number(m) * 60 + Number(s);
};

const cues = lines.map((l, i) => {
  // Dialogue: 0,0:00:00.20,0:00:04.00,Default,,0,0,0,,text
  const parts = l.replace(/^Dialogue:\s*/, "").split(",");
  const start = toSec(parts[1]);
  const end = toSec(parts[2]);
  const txt = parts.slice(9).join(",").trim();
  return { i, start, end, txt };
});

console.log(`Found ${cues.length} cues`);

const VOICE = process.env.VOICE || "Meijia";
const RATE = process.env.RATE || "190"; // wpm

for (const c of cues) {
  const aiff = join(OUT_DIR, `n${String(c.i).padStart(2, "0")}.aiff`);
  const wav = join(OUT_DIR, `n${String(c.i).padStart(2, "0")}.wav`);
  execFileSync("say", ["-v", VOICE, "-r", RATE, "-o", aiff, c.txt]);
  execFileSync(FFMPEG, ["-y", "-loglevel", "error", "-i", aiff, "-ar", "48000", "-ac", "2", wav]);
  const dur = mediaDuration(wav);
  c.wav = wav;
  c.dur = dur;
  console.log(`  ${c.i} [${c.start.toFixed(2)}s] dur=${dur.toFixed(2)}s : ${c.txt}`);
}

const cuesPath = project.out("tts/cues.json");
writeFileSync(cuesPath, JSON.stringify(cues, null, 2));
console.log(`Wrote ${cuesPath}`);
