"""Deterministic error-class classifier for REFUTED verdicts.

The classifier maps a REFUTED finding's signal vector to a taxonomy class. The
decision rules are a fixed priority list over strong, defensible regex signals;
anything that fires no rule is a ``TRUE_CANDIDATE`` (ranked by ``score``, not
classified away). Deterministic and auditable by construction.
"""

from __future__ import annotations

from docassay.triage import taxonomy
from docassay.triage.signals import FindingSignals


def classify(signals: FindingSignals) -> str:
    """Classify a REFUTED finding into a taxonomy class (first match wins)."""
    if signals.perf_note and signals.versioned:
        return taxonomy.PERF_NOTE
    if signals.capability:
        return taxonomy.CAPABILITY_STATEMENT
    if signals.foreign_subject:
        return taxonomy.SUBJECT_MISATTRIBUTION
    if signals.config_value:
        return taxonomy.CONFIG_VALUE
    if signals.external_reference:
        return taxonomy.EXTERNAL_REFERENCE
    if signals.module_relative:
        return taxonomy.MODULE_RELATIVE
    if signals.template_path:
        return taxonomy.TEMPLATE_PATH
    if signals.runtime_namespace:
        return taxonomy.RUNTIME_VALUE
    return taxonomy.TRUE_CANDIDATE
