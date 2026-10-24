import { useEffect, useMemo, useState } from "react";
import { fetchBundleStream, fetchLog, type ProgressEvent } from "../api";
import type { Assertion, Bundle, Referent } from "../types";
import AssertionCard from "../components/AssertionCard";
import FilterBar, { DEFAULT_FILTERS, type Filters } from "../components/FilterBar";
import ProvenanceViewer from "../components/ProvenanceViewer";
import SummaryCards from "../components/SummaryCards";
import { IconArrowLeft, IconClose, IconSearch, IconShield } from "../components/icons";
import { PhaseChips, phaseLabel, type PhaseTiming } from "../components/ui";
import AnalyzingLog, { type LogLine } from "../components/AnalyzingLog";

function toLogLine(evt: ProgressEvent): LogLine {
  return { kind: (evt.kind as LogLine["kind"]) || "info", message: evt.message };
}

interface ProvenanceTarget {
  source: string;
  start: number | null;
  end: number | null;
  title: string;
}

interface AssertionRow {
  referent: Referent;
  assertion: Assertion;
  key: string;
}

interface Props {
  repoId: string;
  onBack: () => void;
}

export default function RepoView({ repoId, onBack }: Props) {
  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [target, setTarget] = useState<ProvenanceTarget | null>(null);
  const [logEvents, setLogEvents] = useState<LogLine[]>([]);
  const [phases, setPhases] = useState<PhaseTiming[]>([]);
  const [runId, setRunId] = useState(0);
  const [showLog, setShowLog] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setBundle(null);
    setLogEvents([]);
    setPhases([]);
    setShowLog(false);
    setRunId((r) => r + 1);
    const onProgress = (evt: ProgressEvent) => {
      // Phase timing frames feed the phase summary, not the scrolling log.
      if (evt.kind === "timing" && typeof evt.duration_ms === "number") {
        setPhases((prev) => [
          ...prev,
          { label: phaseLabel(evt.message), ms: evt.duration_ms as number },
        ]);
        return;
      }
      setLogEvents((prev) => [...prev, toLogLine(evt)]);
    };
    void fetchBundleStream(repoId, onProgress)
      .then(async (b) => {
        setBundle(b);
        // A cached bundle streams no progress, so restore the run's persisted
        // log; a live run already populated it from the stream. The persisted
        // timing frames restore the phase summary on a cached open too.
        const stored = await fetchLog(repoId).catch(() => [] as ProgressEvent[]);
        const storedLines = stored.filter((e) => e.kind !== "timing");
        const storedPhases = stored
          .filter((e) => e.kind === "timing" && typeof e.duration_ms === "number")
          .map((e) => ({ label: phaseLabel(e.message), ms: e.duration_ms as number }));
        setLogEvents((prev) => (prev.length > 0 ? prev : storedLines.map(toLogLine)));
        setPhases((prev) => (prev.length > 0 ? prev : storedPhases));
      })
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, [repoId]);

  const predicates = useMemo(
    () => Array.from(new Set((bundle?.referents ?? []).map((r) => r.predicate_type))).sort(),
    [bundle],
  );

  const domains = useMemo(
    () =>
      Array.from(new Set((bundle?.referents ?? []).map((r) => r.domain))).sort((a, b) =>
        a.localeCompare(b),
      ),
    [bundle],
  );

  const rows = useMemo<AssertionRow[]>(() => {
    if (!bundle) return [];
    const q = filters.search.trim().toLowerCase();
    const out: AssertionRow[] = [];
    for (const r of bundle.referents) {
      if (filters.predicate && r.predicate_type !== filters.predicate) continue;
      if (filters.domain && r.domain !== filters.domain) continue;
      if (
        q &&
        !r.object.toLowerCase().includes(q) &&
        !r.domain.toLowerCase().includes(q)
      )
        continue;
      for (const a of r.assertions) {
        if (filters.verdict && a.code_verdict !== filters.verdict) continue;
        out.push({
          referent: r,
          assertion: a,
          key: `${r.predicate_type}|${r.object}|${a.context.version ?? ""}|${a.claims[0]?.claim_id ?? ""}`,
        });
      }
    }
    return out;
  }, [bundle, filters]);

  const open = (source: string, start: number | null, end: number | null, title: string) => {
    setTarget({ source, start, end, title });
  };

  const total = bundle?.referents.reduce((n, r) => n + r.assertions.length, 0) ?? 0;

  return (
    <div className="page">
      <header className="topbar">
        <button className="ghost back icon-btn" onClick={onBack}>
          <IconArrowLeft size={15} />
          repositories
        </button>
        {bundle && logEvents.length > 0 && (
          <button className="ghost icon-btn" onClick={() => setShowLog(true)} title="View analysis log">
            <IconSearch size={14} />
            View logs
          </button>
        )}
        {bundle && !loading && phases.length > 0 && (
          <span className="run-phases" title="analysis phase timings">
            <PhaseChips phases={phases} />
          </span>
        )}
        {bundle && (
          <div className="brand">
            <span className="brand-mark">
              <IconShield size={18} />
            </span>
            <span className="brand-text">
              <h1>{bundle.meta.repo}</h1>
              <span className="sub">
                {bundle.meta.claims} claims · {bundle.meta.evidence} evidence · tool v
                {bundle.meta.tool_version}
              </span>
            </span>
          </div>
        )}
      </header>

      {loading && logEvents.length > 0 && (
        <AnalyzingLog
          key={runId}
          title="Analyzing repository"
          events={logEvents}
          pending
          phases={phases}
        />
      )}
      {error && <div className="error">{error}</div>}

      {bundle && (
        <>
          <SummaryCards meta={bundle.meta} />

          <section className="panel">
            <FilterBar
              predicates={predicates}
              domains={domains}
              filters={filters}
              onChange={setFilters}
            />
            <div className="muted tiny result-count">
              showing <strong>{rows.length}</strong> of {total} assertions
            </div>
          </section>

          <section className="assertions">
            {rows.length === 0 && <div className="empty-state">No matching assertions.</div>}
            {rows.map((row) => (
              <AssertionCard
                key={row.key}
                referent={row.referent}
                assertion={row.assertion}
                evidence={bundle.evidence}
                onOpen={open}
              />
            ))}
          </section>
        </>
      )}

      {target && (
        <ProvenanceViewer
          key={`${target.source}:${target.start}:${target.end}`}
          repoId={repoId}
          source={target.source}
          start={target.start}
          end={target.end}
          title={target.title}
          onClose={() => setTarget(null)}
        />
      )}

      {showLog && (
        <div className="modal-overlay" onClick={() => setShowLog(false)}>
          <div className="modal log-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-head">
              <strong>
                <IconSearch size={15} />
                Analysis log
              </strong>
              <span className="muted small">{bundle?.meta.repo}</span>
              <button className="close" onClick={() => setShowLog(false)} aria-label="close">
                <IconClose size={18} />
              </button>
            </div>
            <div className="modal-body">
              <AnalyzingLog title="Analyzing repository" events={logEvents} phases={phases} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}