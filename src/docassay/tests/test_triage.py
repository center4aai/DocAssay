"""Tests for the triage layer: signals, classifier, score, sampling, findings."""

from __future__ import annotations

from docassay.core.models import Context, PredicateClaim
from docassay.predicates.dependency import dependency_predicate
from docassay.predicates.listing import path_exists_predicate
from docassay.triage import taxonomy
from docassay.triage.classifier import classify
from docassay.triage.score import score_finding
from docassay.triage.signals import (
    classify_document,
    compute_signals,
    finding_level,
)


def _claim(
    raw_context: str,
    *,
    object: str = "python",
    predicate: str = "DEPENDENCY",
    version: str | None = None,
    polarity: frozenset[str] = frozenset(),
    source: str = "README.md",
) -> PredicateClaim:
    return PredicateClaim(
        claim_id=f"{source}:1:0",
        source=source,
        predicate_type=predicate,
        object=object,
        raw_context=raw_context,
        context=Context(version=version, polarity=polarity),
    )


def _signals(raw_context: str, *, object: str = "python", **kw) -> dict:
    from docassay.core.models import Assertion

    claim = _claim(raw_context, object=object, **kw)
    assertion = Assertion(
        predicate_type=claim.predicate_type,
        object=claim.object,
        domain="",
        claims=(claim,),
        context=claim.context,
        code_verdict="REFUTED",
        code_conflicts=(claim.claim_id,),
    )
    predicate = (
        dependency_predicate if claim.predicate_type == "DEPENDENCY" else path_exists_predicate
    )
    return compute_signals(assertion, predicate).to_dict()


# --- document classification --------------------------------------------------


def test_classify_document_readme():
    assert classify_document("README.md") == "README"
    assert classify_document("docs/README.rst") == "README"


def test_classify_document_directive():
    assert classify_document("CONTRIBUTING.md") == "DIRECTIVE"
    assert classify_document("docs/MAINTAINERS.rst") == "DIRECTIVE"


def test_classify_document_benchmark_and_test():
    assert classify_document("dev/benchmarks/gateway.md") == "BENCHMARK"
    assert classify_document("tests/db/note.md") == "TEST"


# --- signals: discriminative error classes ------------------------------------


def test_signal_foreign_subject_article():
    s = _signals(
        "the ONNX runtime does not require python",
        object="python",
        polarity=frozenset({"not"}),
    )
    assert s["foreign_subject"] is True


def test_signal_subject_only_support():
    s = _signals("Django-Celery only supports Celery 4.0 and below", object="celery")
    assert s["foreign_subject"] is True


def test_signal_capability_statement():
    s = _signals(
        "From Django 5.1+ there is built-in support for connection pooling",
        object="django",
        version=">=5.1",
    )
    assert s["capability"] is True


def test_signal_perf_note():
    s = _signals("faster with PyTorch 2.9 or later", object="pytorch", version=">=2.9")
    assert s["perf_note"] is True


def test_signal_module_relative():
    s = _signals(
        "the airflow.providers.common.sql module",
        object="airflow.providers.common.sql",
        predicate="PATH_EXISTS",
    )
    assert s["module_relative"] is True


def test_signal_runtime_namespace():
    s = _signals(
        "the default value is `airflow/connections`",
        object="airflow/connections",
        predicate="PATH_EXISTS",
    )
    assert s["runtime_namespace"] is True


def test_signal_external_reference_single_dot():
    s = _signals(
        "`modern-sql.com/standard`_: has a discussion",
        object="modern-sql.com/standard",
        predicate="PATH_EXISTS",
    )
    assert s["external_reference"] is True


# --- classifier ---------------------------------------------------------------


def test_classify_perf_note_wins():
    signals = compute_signals(
        _assertion(_claim("faster with PyTorch 2.9 or later", object="pytorch", version=">=2.9")),
        dependency_predicate,
    )
    assert classify(signals) == taxonomy.PERF_NOTE


def test_classify_true_candidate_default():
    signals = compute_signals(
        _assertion(_claim("Python 3.9.1 is required", object="python", version="==3.9.1")),
        dependency_predicate,
    )
    assert classify(signals) == taxonomy.TRUE_CANDIDATE


# --- score --------------------------------------------------------------------


def test_score_penalizes_systematic_noise():
    signals = compute_signals(
        _assertion(
            _claim(
                "the ONNX runtime does not require python",
                object="python",
                polarity=frozenset({"not"}),
            )
        ),
        dependency_predicate,
    )
    cls = classify(signals)
    assert cls == taxonomy.SUBJECT_MISATTRIBUTION
    score, _ = score_finding(signals, cls)
    assert score < 0.5


def test_score_ranks_candidate_above_noise():
    candidate = compute_signals(
        _assertion(_claim("Python 3.9.1 is required", object="python", version="==3.9.1")),
        dependency_predicate,
    )
    noise = compute_signals(
        _assertion(
            _claim(
                "the ONNX runtime does not require python",
                object="python",
                polarity=frozenset({"not"}),
            )
        ),
        dependency_predicate,
    )
    assert (
        score_finding(candidate, taxonomy.TRUE_CANDIDATE)[0]
        > score_finding(noise, taxonomy.SUBJECT_MISATTRIBUTION)[0]
    )


# --- sampling ------------------------------------------------------------------


def test_stratified_estimate_reviews_all():
    from docassay.triage.sampling import stratified_estimate

    sizes = {("DEPENDENCY", "TRUE_CANDIDATE", False): 10}
    reviewed = {("DEPENDENCY", "TRUE_CANDIDATE", False): 10}
    correct = {("DEPENDENCY", "TRUE_CANDIDATE", False): 9}
    estimate, ci, reviewed_n, total = stratified_estimate(sizes, reviewed, correct)
    assert estimate == 0.9
    assert total == 10
    assert reviewed_n == 10
    assert ci[0] <= 0.9 <= ci[1]


def test_wilson_interval_bounds():
    from docassay.triage.sampling import wilson_interval

    lo, hi = wilson_interval(9, 10)
    assert 0.0 <= lo <= 0.9 <= hi <= 1.0
    lo0, hi0 = wilson_interval(0, 0)
    assert (lo0, hi0) == (0.0, 1.0)


def _assertion(claim: PredicateClaim):
    from docassay.core.models import Assertion

    return Assertion(
        predicate_type=claim.predicate_type,
        object=claim.object,
        domain="",
        claims=(claim,),
        context=claim.context,
        code_verdict="REFUTED",
        code_conflicts=(claim.claim_id,),
    )


# --- finding levels ------------------------------------------------


def test_finding_level_tiers() -> None:
    top = frozenset({"src", "docs"})
    # A path whose first segment exists in the listing is anchored.
    assert (
        finding_level("PATH_EXISTS", "src/old/utils.py", "the `src/old/utils.py`", top)
        == "anchored"
    )
    assert finding_level("PATH_EXISTS", "old/utils.py", "the `old/utils.py`", top) == "unanchored"
    # A bare name is level 2.
    assert finding_level("PATH_EXISTS", "config.py", "the `config.py`", top) == "bare"
    # A relative Markdown link target is anchored even without a repo first segment.
    assert finding_level("PATH_EXISTS", "api.md", "see [api](api.md)", top) == "anchored"
    assert (
        finding_level("PATH_EXISTS", "x/y.md", "see [x](https://example.com/y.md)", top)
        == "unanchored"
    )
    # Non-path predicates carry no tier.
    assert finding_level("DEPENDENCY", "python", "requires python", top) == "-"


def test_anchored_score_above_bare() -> None:
    from docassay.core.models import Assertion

    claim = _claim(
        "the `src/old/utils.py` file", object="src/old/utils.py", predicate="PATH_EXISTS"
    )
    assertion = Assertion(
        predicate_type="PATH_EXISTS",
        object=claim.object,
        domain="",
        claims=(claim,),
        context=claim.context,
        code_verdict="REFUTED",
        code_conflicts=(claim.claim_id,),
    )
    anchored = compute_signals(assertion, path_exists_predicate, top_levels=frozenset({"src"}))
    bare_claim = _claim("the `config.py` file", object="config.py", predicate="PATH_EXISTS")
    bare_assertion = Assertion(
        predicate_type="PATH_EXISTS",
        object=bare_claim.object,
        domain="",
        claims=(bare_claim,),
        context=bare_claim.context,
        code_verdict="REFUTED",
        code_conflicts=(bare_claim.claim_id,),
    )
    bare = compute_signals(bare_assertion, path_exists_predicate, top_levels=frozenset({"src"}))
    assert anchored.finding_level == "anchored"
    assert bare.finding_level == "bare"
    assert (
        score_finding(anchored, taxonomy.TRUE_CANDIDATE)[0]
        > score_finding(bare, taxonomy.TRUE_CANDIDATE)[0]
    )


def test_report_location_uses_source_not_window_index() -> None:
    # ``primary_claim_id`` is ``{source}:{window}:{offset}``; the report must
    # not leak the window index into the displayed path.
    from docassay.triage.findings import Finding
    from docassay.triage.report import _claim_line

    finding = Finding(
        finding_id="PATH_EXISTS|src/a.py|",
        repo="demo",
        predicate="PATH_EXISTS",
        object="src/a.py",
        domain="",
        verdict="REFUTED",
        predicted_class=taxonomy.TRUE_CANDIDATE,
        score=1.0,
        score_breakdown={},
        primary_source="docs/install.md",
        primary_claim_id="docs/install.md:18:26",
        primary_line_start=26,
        primary_line_end=26,
    )
    assert _claim_line(finding) == "docs/install.md"
