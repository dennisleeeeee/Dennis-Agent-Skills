import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";

export type Seg = {
  srcStart: number;
  srcEnd: number;
  rate: number;
  name: string;
  // Optional zoom-in (e.g. to make typing / code readable). zoom>1 scales the
  // frame up around a focal point. Rendered server-side by Remotion (CSS
  // transform is respected, unlike CSS blur/backdrop-filter on video).
  zoom?: number; // target scale, >1 to zoom in (default 1 = no zoom)
  zoomX?: number; // focal point x, 0..1 (default 0.5 = center)
  zoomY?: number; // focal point y, 0..1 (default 0.5 = center)
  zoomInSec?: number; // smooth ramp-in duration in output sec (default 0 = instant)
  zoomOutSec?: number; // smooth ramp-out at the segment's end (default 0 = hold zoom)
};

// A caption is anchored to a segment (by index) and positioned in *output*
// seconds relative to that segment's start, so it stays in sync no matter how
// the segment's playback rate is tuned.
export type Caption = {
  seg: number; // which segment this caption belongs to
  atSec: number; // seconds into that segment (output time) when it appears
  durSec: number; // how long it stays on screen
  text: string;
  sub?: string; // optional second, smaller line
};

// A privacy blur: a rectangular region (in composition px, e.g. 1456x902 space)
// that gets a strong mosaic/blur so sensitive on-screen text (customer names)
// is unreadable, while the rest of the frame stays sharp. Anchored to a segment
// in output time, like a caption.
export type Blur = {
  seg: number;
  atSec: number;
  durSec: number;
  x: number;
  y: number;
  w: number;
  h: number;
};

export type EditedVideoProps = {
  fps: number;
  overlap: number; // crossfade overlap between adjacent segments (frames)
  sourceFile: string; // path under public/, e.g. "workiq/source.mp4"
  musicFile?: string; // path under public/, e.g. "workiq/music.mp3"
  musicVolume?: number;
  segments: Seg[];
  captions?: Caption[];
  blurs?: Blur[];
};

const segLen = (s: Seg, fps: number) =>
  Math.max(1, Math.round(((s.srcEnd - s.srcStart) * fps) / s.rate));

const computeStarts = (segments: Seg[], fps: number, overlap: number) => {
  let acc = 0;
  return segments.map((s) => {
    const st = acc;
    acc += segLen(s, fps) - overlap;
    return st;
  });
};

// Total composition length for a given project's props.
export const editedDuration = ({ fps, overlap, segments }: EditedVideoProps) => {
  const starts = computeStarts(segments, fps, overlap);
  const last = segments[segments.length - 1];
  return starts[starts.length - 1] + segLen(last, fps);
};

const Segment: React.FC<{
  seg: Seg;
  index: number;
  len: number;
  total: number;
  fps: number;
  overlap: number;
  sourceFile: string;
}> = ({ seg, index, len, total, fps, overlap, sourceFile }) => {
  const frame = useCurrentFrame();
  const isFirst = index === 0;
  const isLast = index === total - 1;

  const fadeInDur = isFirst ? 18 : overlap;
  let opacity = interpolate(frame, [0, fadeInDur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  if (isLast) {
    const fadeOut = interpolate(frame, [len - 30, len], [1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    opacity = Math.min(opacity, fadeOut);
  }

  const targetZoom = seg.zoom ?? 1;
  const zx = (seg.zoomX ?? 0.5) * 100;
  const zy = (seg.zoomY ?? 0.5) * 100;
  const rampIn = Math.round((seg.zoomInSec ?? 0) * fps);
  const rampOut = Math.round((seg.zoomOutSec ?? 0) * fps);
  // Build an eased in -> hold -> out zoom curve. Keyframes must be strictly
  // increasing, so we assemble them conditionally.
  let scale = targetZoom;
  if (targetZoom !== 1) {
    const kf: number[] = [];
    const vals: number[] = [];
    if (rampIn > 0) {
      kf.push(0, rampIn);
      vals.push(1, targetZoom);
    } else {
      kf.push(0);
      vals.push(targetZoom);
    }
    const outStart = len - rampOut;
    if (rampOut > 0 && outStart > kf[kf.length - 1]) {
      kf.push(outStart, len);
      vals.push(targetZoom, 1);
    }
    scale =
      kf.length > 1
        ? interpolate(frame, kf, vals, {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.inOut(Easing.ease),
          })
        : targetZoom;
  }

  return (
    <AbsoluteFill style={{ backgroundColor: "black", opacity }}>
      <AbsoluteFill
        style={{
          transform: `scale(${scale})`,
          transformOrigin: `${zx}% ${zy}%`,
        }}
      >
        <OffthreadVideo
          src={staticFile(sourceFile)}
          trimBefore={Math.round(seg.srcStart * fps)}
          trimAfter={Math.round(seg.srcEnd * fps)}
          playbackRate={seg.rate}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const CJK_FONT =
  '"PingFang TC", "PingFang SC", "Hiragino Sans GB", "Microsoft JhengHei", "Noto Sans CJK TC", system-ui, -apple-system, sans-serif';

// A lower-third caption: fades/slides in, holds, then fades out.
const Caption: React.FC<{ caption: Caption; len: number; fps: number }> = ({
  caption,
  len,
  fps,
}) => {
  const frame = useCurrentFrame();
  const fade = Math.min(8, Math.round(fps * 0.25));
  const opacity =
    interpolate(frame, [0, fade], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }) *
    interpolate(frame, [len - fade, len], [1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  const slide = interpolate(frame, [0, fade], [16, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: "7%",
        opacity,
      }}
    >
      <div
        style={{
          transform: `translateY(${slide}px)`,
          maxWidth: "82%",
          textAlign: "center",
          background: "linear-gradient(180deg, rgba(10,16,32,0.82), rgba(10,16,32,0.92))",
          borderLeft: "5px solid #4aa3ff",
          borderRadius: 12,
          padding: "16px 28px",
          boxShadow: "0 10px 36px rgba(0,0,0,0.45)",
        }}
      >
        <div
          style={{
            fontFamily: CJK_FONT,
            color: "#ffffff",
            fontSize: 34,
            fontWeight: 700,
            lineHeight: 1.3,
            letterSpacing: 0.5,
          }}
        >
          {caption.text}
        </div>
        {caption.sub ? (
          <div
            style={{
              fontFamily: CJK_FONT,
              color: "#aacbff",
              fontSize: 24,
              fontWeight: 500,
              marginTop: 8,
              lineHeight: 1.3,
            }}
          >
            {caption.sub}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

export const EditedVideo: React.FC<EditedVideoProps> = (props) => {
  const { fps, overlap, segments, sourceFile, musicFile, musicVolume, captions } =
    props;
  const starts = computeStarts(segments, fps, overlap);

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {segments.map((s, i) => {
        const len = segLen(s, fps);
        return (
          <Sequence
            key={i}
            from={starts[i]}
            durationInFrames={len}
            name={s.name}
          >
            <Segment
              seg={s}
              index={i}
              len={len}
              total={segments.length}
              fps={fps}
              overlap={overlap}
              sourceFile={sourceFile}
            />
          </Sequence>
        );
      })}
      {(captions ?? []).map((c, i) => {
        const base = starts[c.seg] ?? 0;
        const from = base + Math.round(c.atSec * fps);
        const len = Math.max(1, Math.round(c.durSec * fps));
        return (
          <Sequence key={`cap-${i}`} from={from} durationInFrames={len} name={`Caption ${i + 1}`}>
            <Caption caption={c} len={len} fps={fps} />
          </Sequence>
        );
      })}
      {musicFile ? (
        <Audio src={staticFile(musicFile)} volume={musicVolume ?? 0.85} />
      ) : null}
    </AbsoluteFill>
  );
};
