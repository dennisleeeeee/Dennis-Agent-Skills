// Generates an original, royalty-free "tech demo" background track for a project.
// Pure synthesis with ffmpeg (sine layers + kick/hat), so there are no licensing concerns.
// Swap it freely: just replace the project's music file with any track of your choice.
//
// Usage: node scripts/makeMusic.mjs <project-name> [durationSeconds]
import { execFileSync } from "node:child_process";
import { loadProject, FFMPEG } from "./lib/project.mjs";

const project = loadProject();
const TOTAL = Number(process.argv[3] || process.env.DURATION || 73.5);
const SR = 48000;
const BPM = 120;
const beat = 60 / BPM; // 0.5s
const bar = beat * 4; // 2s
const BARS = 8;
const LOOP = bar * BARS; // 16s

const midi = (m) => 440 * Math.pow(2, (m - 69) / 12);

// i - VI - III - VII in A minor: Am F C G  (bright, "techy" progression)
const chords = [
  [57, 60, 64], // Am
  [53, 57, 60], // F
  [60, 64, 67], // C
  [55, 59, 62], // G
  [57, 60, 64],
  [53, 57, 60],
  [60, 64, 67],
  [55, 59, 62],
];
const bassRoots = [45, 41, 48, 43, 45, 41, 48, 43]; // A2 F2 C3 G2 ...

const inputs = []; // { type, freq?/expr?, dur }
const notes = []; // { idx, delayMs, dur, att, rel, gain }

const addTone = (freq, startSec, dur, gain, att, rel) => {
  const idx = inputs.length;
  inputs.push({ type: "sine", freq, dur });
  notes.push({ idx, delayMs: Math.round(startSec * 1000), dur, att, rel, gain });
};

for (let b = 0; b < BARS; b++) {
  const t0 = b * bar;
  const ch = chords[b];
  // Pad: sustained chord across the bar
  for (const m of ch) addTone(midi(m), t0, bar, 0.08, 0.35, 0.5);
  // Bass: root, one whole bar
  addTone(midi(bassRoots[b]), t0, bar, 0.16, 0.04, 0.3);
  // Arpeggio: quarter notes root -> fifth -> octave -> third
  const arp = [ch[0], ch[2], ch[0] + 12, ch[1]];
  for (let q = 0; q < 4; q++) {
    addTone(midi(arp[q]), t0 + q * beat, 0.46, 0.085, 0.01, 0.16);
  }
}

// Four-on-the-floor kick (decaying 55Hz pulse every beat)
const kickIdx = inputs.length;
inputs.push({
  type: "expr",
  expr: `0.55*exp(-mod(t\\,${beat})*9)*sin(2*PI*55*t)`,
  dur: LOOP,
});
// Offbeat hi-hat (filtered noise burst on the "and")
const hatIdx = inputs.length;
inputs.push({
  type: "expr",
  expr: `0.3*random(0)*exp(-mod(t-${beat / 2}\\,${beat})*45)`,
  dur: LOOP,
});

const inputArgs = [];
for (const inp of inputs) {
  inputArgs.push("-f", "lavfi", "-t", String(inp.dur));
  if (inp.type === "sine") {
    inputArgs.push("-i", `sine=frequency=${inp.freq.toFixed(3)}:sample_rate=${SR}`);
  } else {
    inputArgs.push("-i", `aevalsrc=exprs=${inp.expr}:s=${SR}:d=${inp.dur}`);
  }
}

const fparts = [];
const labels = [];
for (const n of notes) {
  const outStart = Math.max(0, n.dur - n.rel).toFixed(3);
  fparts.push(
    `[${n.idx}:a]afade=t=in:st=0:d=${n.att},afade=t=out:st=${outStart}:d=${n.rel},` +
      `volume=${n.gain},adelay=delays=${n.delayMs}:all=1[n${n.idx}]`,
  );
  labels.push(`[n${n.idx}]`);
}
fparts.push(`[${kickIdx}:a]volume=1.0[kick]`);
labels.push("[kick]");
fparts.push(`[${hatIdx}:a]highpass=f=6000,volume=1.0[hat]`);
labels.push("[hat]");
fparts.push(
  `${labels.join("")}amix=inputs=${labels.length}:normalize=0:dropout_transition=0[mix]`,
);
fparts.push(
  `[mix]atrim=0:${LOOP},highpass=f=35,lowpass=f=15000,aecho=0.85:0.75:55:0.2,alimiter=limit=0.9[loop]`,
);
const filter = fparts.join(";");

console.log(`Building 16s loop from ${inputs.length} sources...`);
const loopWav = project.out("_music_loop.wav");
execFileSync(
  FFMPEG,
  [
    "-y", "-hide_banner", "-loglevel", "error",
    ...inputArgs,
    "-filter_complex", filter,
    "-map", "[loop]", "-ac", "1", "-ar", String(SR),
    loopWav,
  ],
  { stdio: "inherit" },
);

const reps = Math.ceil(TOTAL / LOOP) + 1;
console.log(`Looping x${reps} and mastering to ${TOTAL}s -> ${project.music}`);
execFileSync(
  FFMPEG,
  [
    "-y", "-hide_banner", "-loglevel", "error",
    "-stream_loop", String(reps), "-i", loopWav,
    "-af",
    `atrim=0:${TOTAL},asetpts=N/SR/TB,` +
      `afade=t=in:st=0:d=1.5,afade=t=out:st=${(TOTAL - 2.8).toFixed(2)}:d=2.8,` +
      `acompressor=threshold=-20dB:ratio=3:attack=20:release=250,` +
      `loudnorm=I=-15:TP=-1.5:LRA=11,alimiter=limit=0.95`,
    "-ac", "2", "-ar", "44100", "-b:a", "192k",
    project.music,
  ],
  { stdio: "inherit" },
);

console.log(`Done: ${project.music}`);
