import { Composition } from "remotion";
import { EditedVideo, editedDuration } from "./EditedVideo";
import { EDITING_PROJECTS } from "./projects";

// One <Composition> per real-recording editing project (see src/projects.ts).
export const RemotionRoot: React.FC = () => {
  return (
    <>
      {EDITING_PROJECTS.map((p) => (
        <Composition
          key={p.id}
          id={p.id}
          component={EditedVideo}
          durationInFrames={editedDuration(p)}
          fps={p.fps}
          width={p.width}
          height={p.height}
          defaultProps={{
            fps: p.fps,
            overlap: p.overlap,
            sourceFile: p.sourceFile,
            musicFile: p.musicFile,
            musicVolume: p.musicVolume,
            segments: p.segments,
            captions: p.captions,
          }}
        />
      ))}
    </>
  );
};
