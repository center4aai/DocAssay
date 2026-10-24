"""Finding triage: aggregation and prioritization of verdicts under noise.

The tool resolves thousands of assertions per repository; a human cannot review
them line by line. This package turns the resolved assertions into a reviewable
surface:

- ``signals`` — a deterministic per-finding signal vector (world, negation,
  document class, downgrade markers, discriminative error-class regexes);
- ``taxonomy`` — the error-class vocabulary from the internal DEPENDENCY and
  STRUCTURE precision audits;
- ``classifier`` — a deterministic classifier of a REFUTED verdict into a
  systematic error class or ``TRUE_CANDIDATE``;
- ``score`` — a transparent finding-quality score that ranks candidates;
- ``sampling`` — stratified precision estimation (measurement without a full
  census) with Wilson intervals;
- ``report`` — the per-repository triage report (top findings + noise budget);
- ``adjudicate`` — the human review loop (labels → precision + confirmed list).

Everything here is deterministic and advisory: it never changes a verdict and
does not touch the faithfulness invariant (methodology §6.3).
"""
