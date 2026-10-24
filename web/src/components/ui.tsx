import type { ClaimContext } from "../types";
import { IconCheck, IconX, IconFile } from "./icons";

const VERDICT_META: Record<string, { label: string; icon?: React.ReactNode }> = {
  SUPPORTED: { label: "SUPPORTED", icon: <IconCheck size={12} /> },
  REFUTED: { label: "REFUTED", icon: <IconX size={12} /> },
  NEI: { label: "NEI", icon: <IconFile size={12} /> },
};

export function VerdictBadge({ verdict }: { verdict: string | null }) {
  const key = verdict ?? "none";
  const meta = VERDICT_META[key];
  const label = verdict ?? "n/a";
  return (
    <span className={`badge verdict-${key.toLowerCase()}`}>
      {meta?.icon}
      {label}
    </span>
  );
}

export function DomainChip({ domain }: { domain: string }) {
  if (!domain) return null;
  return <span className="chip chip-domain" title="domain">{domain}</span>;
}

export function ContextChips({ context }: { context: ClaimContext }) {
  const chips: { label: string; value: string }[] = [];
  if (context.version) chips.push({ label: "version", value: context.version });
  for (const key of ["platform", "polarity", "restriction", "time", "arch"] as const) {
    for (const value of context[key] ?? []) chips.push({ label: key, value });
  }
  if (chips.length === 0) return <span className="muted tiny">no context markers</span>;
  return (
    <span className="chips">
      {chips.map((c, i) => (
        <span key={i} className={`chip chip-${c.label}`}>
          {c.value}
        </span>
      ))}
    </span>
  );
}

export function locLabel(source: string, start: number | null, end: number | null): string {
  if (start !== null) return `${source}:${start}-${end ?? start}`;
  return source;
}

export interface PhaseTiming {
  label: string;
  ms: number;
}

const PHASE_LABELS: Record<string, string> = {
  clone: "Clone",
  extract: "Extract",
  analyze: "Analyze",
};

export function phaseLabel(phase: string): string {
  return PHASE_LABELS[phase] ?? phase;
}

export function formatDuration(ms: number): string {
  const seconds = ms / 1000;
  if (seconds < 60) return `${seconds.toFixed(1)} s`;
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  return `${m} m ${String(s).padStart(2, "0")} s`;
}

export function PhaseChips({ phases }: { phases: PhaseTiming[] }) {
  if (phases.length === 0) return null;
  return (
    <span className="phase-chips">
      {phases.map((p, i) => (
        <span key={i} className="phase-chip">
          {p.label} <strong>{formatDuration(p.ms)}</strong>
        </span>
      ))}
    </span>
  );
}

export function monogram(name: string): string {
  const clean = name.replace(/[._-]/g, " ").trim();
  if (!clean) return "R";
  const parts = clean.split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}