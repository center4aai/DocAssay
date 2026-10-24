export interface Meta {
  repo: string;
  project_root: string;
  scanned_documents: number;
  created: string;
  tool_version: string;
  claims: number;
  referents: number;
  evidence: number;
  verdicts: Record<string, number>;
  doc_consistency: Record<string, number>;
  resolved: number;
  coverage: number;
}

export interface ClaimContext {
  version: string | null;
  platform: string[];
  polarity: string[];
  restriction: string[];
  time: string[];
  arch: string[];
}

export interface Claim {
  claim_id: string;
  source: string;
  predicate_type: string;
  object: string;
  domain: string;
  raw_context: string;
  context: ClaimContext;
  negative: boolean;
  extraction_source: string;
  anchor_type: string;
  line_start: number | null;
  line_end: number | null;
}

export interface Assertion {
  context: ClaimContext;
  code_verdict: string | null;
  code_verdict_layer: string;
  code_verdict_reason: string;
  is_code_verifiable: boolean;
  code_conflicts: string[];
  evidence_sources: string[];
  supporting_evidence: string[];
  refuting_evidence: string[];
  claims: Claim[];
}

export interface Referent {
  predicate_type: string;
  object: string;
  domain: string;
  doc_consistency: string | null;
  doc_conflicts: string[][];
  assertions: Assertion[];
}

export interface EvidenceRecord {
  source_file: string | null;
  domain: string;
  line_start: number | null;
  line_end: number | null;
  kind: string | null;
  snippet: string;
}

export interface Finding {
  finding_id: string;
  repo: string;
  predicate: string;
  object: string;
  domain: string;
  verdict: string | null;
  doc_consistency: string | null;
  signals: Record<string, unknown>;
  primary_source: string;
  primary_claim_id: string;
  primary_line_start: number | null;
  primary_line_end: number | null;
  raw_context: string;
  refuting_evidence: string[];
  supporting_evidence: string[];
  occurrences: number;
}

export interface Bundle {
  meta: Meta;
  referents: Referent[];
  evidence: Record<string, EvidenceRecord>;
  findings: Finding[];
}

export interface RepoInfo {
  id: string;
  name: string;
  kind: string;
  source: string;
  url?: string | null;
  analyzed: boolean;
  analyzed_at: string | null;
  meta: Meta | null;
}