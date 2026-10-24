import { useEffect, useRef, useState } from "react";
import { IconSearch } from "./icons";
import { PhaseChips, type PhaseTiming } from "./ui";

export type LogKind = "cmd" | "ok" | "info" | "step" | "pulse";

export interface LogLine {
  kind: LogKind;
  message: string;
}

const PREFIX: Record<LogKind, { glyph: string; cls: string }> = {
  cmd: { glyph: "$", cls: "cmd" },
  ok: { glyph: "✓", cls: "ok" },
  info: { glyph: "·", cls: "info" },
  step: { glyph: "→", cls: "step" },
  pulse: { glyph: "…", cls: "pulse" },
};

interface Props {
  title?: string;
  events: LogLine[];
  pending?: boolean;
  percent?: number | null;
  phases?: PhaseTiming[];
}

export default function AnalyzingLog({
  title = "Analyzing",
  events,
  pending = false,
  percent = null,
  phases = [],
}: Props) {
  // Reveal incoming events one line at a time so bursts (fast analyses) still
  // render with a terminal feel instead of a wall of text.
  const [revealed, setRevealed] = useState(0);
  const allShown = revealed >= events.length;
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (allShown) return;
    const t = setTimeout(() => setRevealed((r) => Math.min(events.length, r + 1)), 70);
    return () => clearTimeout(t);
  }, [revealed, allShown, events.length]);

  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight });
  }, [revealed, events.length]);

  const working = pending || !allShown;
  const shown = events.slice(0, revealed);

  return (
    <div className="analyzing">
      <div className="analyzing-head">
        <span className="mac-dots">
          <i />
          <i />
          <i />
        </span>
        <span className="analyzing-title">
          <IconSearch size={15} />
          {title}
        </span>
        <PhaseChips phases={phases} />
        {percent !== null && (
          <span className="analyzing-percent">{Math.round(percent)}%</span>
        )}
      </div>
      {percent !== null && (
        <div
          className="analyze-progress"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(percent)}
        >
          <div
            className="analyze-progress-fill"
            style={{ width: `${Math.min(100, Math.max(0, percent))}%` }}
          />
        </div>
      )}
      <div className="analyzing-body" ref={bodyRef}>
        {shown.map((line, i) => {
          const p = PREFIX[line.kind] ?? PREFIX.info;
          return (
            <div key={i} className={`log-line ${p.cls}`}>
              <span className="log-glyph">{p.glyph}</span>
              <span className="log-text">{line.message}</span>
            </div>
          );
        })}
        {events.length === 0 && (
          <div className="log-line info">
            <span className="log-glyph">·</span>
            <span className="log-text">waiting for the pipeline…</span>
          </div>
        )}
        {working && events.length > 0 && <span className="log-cursor" />}
      </div>
    </div>
  );
}