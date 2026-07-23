import type { EditedVideoProps, Caption, Blur } from "./EditedVideo";

// Registry of every "edited from a real recording" video project.
//
// To add a new editing project (done at bootstrap by the skill):
//   1. create projects/<name>/project.json (see reference.md for the schema)
//   2. drop the source video (+ optional music) under public/<name>/
//   3. import its project.json here and add it to the PROJECT_CONFIGS array below
//
// Example:
//   import myclip from "../projects/myclip/project.json";
//   const PROJECT_CONFIGS = [myclip];

export type EditingProject = EditedVideoProps & {
  id: string;
  width: number;
  height: number;
};

type ProjectConfig = EditingProject & { captions?: Caption[]; blurs?: Blur[] };

// Add each imported project.json to this array.
const PROJECT_CONFIGS: ProjectConfig[] = [];

const fromConfig = (c: ProjectConfig): EditingProject => ({
  id: c.id,
  width: c.width,
  height: c.height,
  fps: c.fps,
  overlap: c.overlap,
  sourceFile: c.sourceFile,
  musicFile: c.musicFile,
  musicVolume: c.musicVolume,
  segments: c.segments,
  captions: c.captions,
  blurs: c.blurs,
});

export const EDITING_PROJECTS: EditingProject[] = PROJECT_CONFIGS.map(fromConfig).filter(
  (p) => p.segments.length > 0,
);
