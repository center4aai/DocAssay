"""Triage vocabulary: error classes and document classes.

The taxonomy is the union of the two precision audits' human categories:

- DEPENDENCY audit: subject-misattribution, capability statement, perf note,
  config value, optionality phrasing, historical, hypothetical,
  test-environment/benchmark.
- STRUCTURE audit: snapshot artifact, ambiguous basename, runtime user config,
  module-relative paths, external/sphinx/build anchors.

The structural downgrade classes (historical, instructional, exemplary,
test_env, locator, conditional, hypothetical, optionality, user_config) are
handled at the predicate layer — a claim carrying one is downgraded to NEI and
never becomes a REFUTED finding. The triage taxonomy below covers the *residual*
REFUTED population, where the audit categories still fire.
"""

from __future__ import annotations

# A REFUTED verdict with no strong systematic-error signal: the plausible real
# doc↔code contradiction, ranked by ``score`` rather than classified away.
TRUE_CANDIDATE = "TRUE_CANDIDATE"

# The negation/version is asserted about a third party, not the project itself
# ("the ONNX runtime does not require python", "Django-Celery only supports
# Celery 4.0 and below").
SUBJECT_MISATTRIBUTION = "SUBJECT_MISATTRIBUTION"

# A version/fact describes a capability of the subject, not a requirement of the
# project ("From Django 5.1+ there is built-in support for connection pooling").
CAPABILITY_STATEMENT = "CAPABILITY_STATEMENT"

# A version mention describes a performance note ("faster with PyTorch 2.9 or
# later"), not a requirement.
PERF_NOTE = "PERF_NOTE"

# The mention is a configuration value / server-side resolution, not a fact
# about the project tree or manifest ("resolves to", "es_compat_with").
CONFIG_VALUE = "CONFIG_VALUE"

# A dotted identifier read as a path is a module reference, not a repo path
# (``airflow.providers.common.sql``).
MODULE_RELATIVE = "MODULE_RELATIVE"

# The path is a runtime/example namespace rather than a repo-tree path
# (``airflow/variables/<name>``, ``BUCKET_1_SRC/subdir``, "the default value is
# ``airflow/connections``").
RUNTIME_VALUE = "RUNTIME_VALUE"

# The path is a template artifact or sits in a template-generated document
# (``foo.jinja2``, ``providers/*/docs/commits.rst``).
TEMPLATE_PATH = "TEMPLATE_PATH"

# The path is absent because the working-tree snapshot is truncated, not because
# the documentation is wrong. Set by the corpus wrapper from a snapshot manifest
# (or by the repeated-reference aggregation signal).
SNAPSHOT_ARTIFACT = "SNAPSHOT_ARTIFACT"

# A path-shaped token that is really a link target or an external reference
# (``modern-sql.com/standard``, Sphinx roles, build/deploy artifacts). The
# predicate layer rejects the common cases (``is_rejectable_path``,
# ``is_sphinx_role_anchor``); this class catches the residuals.
EXTERNAL_REFERENCE = "EXTERNAL_REFERENCE"

# Residual noise not covered by a specific class.
OTHER_NOISE = "OTHER_NOISE"

# Non-finding labels for non-REFUTED items.
SUPPORTED = "SUPPORTED"
ABSTAINED = "ABSTAINED"

# Classes that are known systematic noise: their findings get a score penalty and
# feed the report's noise budget instead of the top list.
SYSTEMATIC_NOISE: frozenset[str] = frozenset(
    {
        SUBJECT_MISATTRIBUTION,
        CAPABILITY_STATEMENT,
        PERF_NOTE,
        CONFIG_VALUE,
        MODULE_RELATIVE,
        RUNTIME_VALUE,
        TEMPLATE_PATH,
        SNAPSHOT_ARTIFACT,
        EXTERNAL_REFERENCE,
        OTHER_NOISE,
    }
)

# Authority ranking of the document a finding was extracted from. Root README and
# directive documents are the most likely to state true current-state claims;
# benchmark and test documents the least.
DOC_AUTHORITY: dict[str, int] = {
    "README": 3,
    "DIRECTIVE": 2,
    "DOCS": 2,
    "TUTORIAL": 1,
    "OTHER": 1,
    "BENCHMARK": 0,
    "TEST": 0,
}
