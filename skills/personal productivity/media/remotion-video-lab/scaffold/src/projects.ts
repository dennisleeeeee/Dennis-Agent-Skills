import type { EditedVideoProps, Caption, Blur } from "./EditedVideo";

// Registry of every "edited from a real recording" video project.
//
// To add a new editing project:
//   1. create projects/<name>/project.json (copy projects/sample)
//   2. drop the source video (+ optional music) under public/<name>/
//   3. import its project.json here and add it to EDITING_PROJECTS
import sample from "../projects/sample/project.json";

export type EditingProject = EditedVideoProps & {
  id: string;
  width: number;
  height: number;
};

type ProjectConfig = EditingProject & { captions?: Caption[]; blurs?: Blur[] };

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

export const EDITING_PROJECTS: EditingProject[] = [sample]
  .map((c) => fromConfig(c as ProjectConfig))
  .filter((p) => p.segments.length > 0);
