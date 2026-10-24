import { useState } from "react";
import type { Assertion, EvidenceRecord, Referent } from "../types";
import { ContextChips, DomainChip, VerdictBadge, locLabel } from "./ui";
import { IconChevronDown } from "./icons";

interface Props {
  referent: Referent;
  assertion: Assertion;
  evidence: Record<string, EvidenceRecord>;
  onOpen: (source: string, start: number | null, end: number | null, title: string) => void;
}

function EvidenceLinks({
  ids,
  evidence,
  tone,
  label,
  onOpen,
}: {
  ids: string[];
  evidence: Record<string, EvidenceRecord>;
  tone: "support" | "refute";
  label: string;
  onOpen: Props["onOpen"];
}) {
  if (ids.length === 0) return null;
  return (
    <div className={`evidence-links ${tone}`}>
      <span className="evidence-links-label">{label}</span>
      {ids.map((id) => {
        const ev = evidence[id];
        const loc = ev ? locLabel(ev.source_file ?? id, ev.line_start, ev.line_end) : id;
        return (
          <div key={id} className="evidence-item">
            <button
              className="evidence-link"
              title={id}
              onClick={() =>
                ev &&
                onOpen(
                  ev.source_file ?? id,
                  ev.line_start,
                  ev.line_end,
                  `evidence · ${id}`,
                )
              }
            >
              {tone === "support" ? "✓ " : "✗ "}
              {loc}
            </button>
            {ev && <DomainChip domain={ev.domain} />}
            {ev?.snippet && <code className="evidence-snippet">{ev.snippet}</code>}
          </div>
        );
      })}
    </div>
  );
}

export default function AssertionCard({ referent, assertion, evidence, onOpen }: Props) {
  // Findings (REFUTED) stay open; SUPPORTED/NEI are collapsed into a compact
  // row so large repositories do not render hundreds of full cards at once.
  const [open, setOpen] = useState<boolean>(assertion.code_verdict === "REFUTED");
  const claimCount = assertion.claims.length;
  const evidenceCount =
    assertion.supporting_evidence.length + assertion.refuting_evidence.length;
  const verdictCls = assertion.code_verdict
    ? ` verdict-${assertion.code_verdict.toLowerCase()}`
    : "";

  return (
    <div className={`assertion${verdictCls}`}>
      <button
        className={`assertion-toggle${open ? " open" : ""}`}
        onClick={() => setOpen((v) => !v)}
      >
        <VerdictBadge verdict={assertion.code_verdict} />
        <span className="assertion-title">
          {referent.predicate_type} · {referent.object}
        </span>
        <DomainChip domain={referent.domain} />
        <ContextChips context={assertion.context} />
        <span className="muted tiny">
          {claimCount} claim{claimCount === 1 ? "" : "s"} · {evidenceCount} evidence
        </span>
        <span className="chevron">
          <IconChevronDown size={16} />
        </span>
      </button>
      {open && (
        <div className="assertion-body">
          {assertion.evidence_sources.length > 0 && (
            <div className="muted tiny">
              evidence sources: {assertion.evidence_sources.join(", ")}
            </div>
          )}
          {assertion.code_verdict === "NEI" &&
            (assertion.code_verdict_layer || assertion.code_verdict_reason) && (
              <div className="nei-note">
                {assertion.code_verdict_layer && (
                  <span className="chip chip-layer">{assertion.code_verdict_layer}</span>
                )}
                {assertion.code_verdict_reason}
              </div>
            )}
          {assertion.code_verdict !== "NEI" && assertion.code_verdict_reason && (
            <div className="nei-note verdict-hint">hint: {assertion.code_verdict_reason}</div>
          )}
          <div className="claims">
            {assertion.claims.map((claim) => (
              <div key={claim.claim_id} className="claim">
                <div className="claim-head">
                  {claim.negative && <span className="badge neg">NEG</span>}
                  <DomainChip domain={claim.domain} />
                  <button
                    className="loc-link"
                    title={claim.claim_id}
                    onClick={() =>
                      onOpen(
                        claim.source,
                        claim.line_start,
                        claim.line_end,
                        `claim · ${claim.source}`,
                      )
                    }
                  >
                    {locLabel(claim.source, claim.line_start, claim.line_end)}
                  </button>
                  <ContextChips context={claim.context} />
                </div>
                <div className="claim-raw">
                  <div className="claim-raw-label">context</div>
                  <div className="claim-raw-text">{claim.raw_context}</div>
                </div>
                <EvidenceLinks
                  ids={assertion.supporting_evidence}
                  evidence={evidence}
                  tone="support"
                  label="supporting evidence"
                  onOpen={onOpen}
                />
                <EvidenceLinks
                  ids={assertion.refuting_evidence}
                  evidence={evidence}
                  tone="refute"
                  label="refuting evidence"
                  onOpen={onOpen}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}