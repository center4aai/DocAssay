"""End-to-end analysis of a repository.

``analyze_repository`` harvests the manifest inventory, scans every documentation
file with the anchor-first extractor, groups claims into assertions, adjudicates
each assertion against the inventory, and computes the cross-document
consistency per referent.
"""

from __future__ import annotations

import dataclasses
import re
import sys
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from docassay.core.assertions import group_into_assertions
from docassay.core.domains import DomainIndex
from docassay.core.models import Assertion, PredicateClaim, ReferentResult
from docassay.core.windows import clear_window_cache
from docassay.data import load_list
from docassay.evidence.git import clear_listing_cache, git_tracked_files
from docassay.evidence.symbols import KIND_MODULE
from docassay.predicates import ALL_PREDICATES
from docassay.predicates.base import Predicate, Verdict
from docassay.vocabularies.structure import SKIPPED_DIRS

_DOC_EXTENSIONS: frozenset[str] = load_list("pipeline.json", "doc_extensions")

# English-only corpus scope (decided 2026-08-28): non-English documents are
# excluded from claim extraction — translations (i18n READMEs, per-language
# docs) are not adjudicated until multilingual markers exist.
_NON_LATIN_RE = re.compile(
    "["
    "\u0370-\u03ff"  # Greek
    "\u0400-\u04ff"  # Cyrillic
    "\u0590-\u05ff"  # Hebrew
    "\u0600-\u06ff"  # Arabic
    "\u0900-\u097f"  # Devanagari
    "\u0980-\u09ff"  # Bengali
    "\u0a00-\u0a7f"  # Gurmukhi
    "\u0a80-\u0aff"  # Gujarati
    "\u0b00-\u0b7f"  # Oriya
    "\u0b80-\u0bff"  # Tamil
    "\u0c00-\u0c7f"  # Telugu
    "\u0c80-\u0cff"  # Kannada
    "\u0d00-\u0d7f"  # Malayalam
    "\u0e00-\u0e7f"  # Thai
    "\u0e80-\u0eff"  # Lao
    "\u0f00-\u0fff"  # Tibetan
    "\u10a0-\u10ff"  # Georgian
    "\u1780-\u17ff"  # Khmer
    "\u3040-\u30ff"  # Hiragana + Katakana
    "\u3400-\u4dbf"  # CJK Extension A
    "\u4e00-\u9fff"  # CJK Unified
    "\uac00-\ud7af"  # Hangul
    "]"
)

# English-only corpus scope: non-English documents are excluded from claim
# extraction. Layer 1 (script ratio) rejects non-Latin scripts (CJK, Cyrillic,
# Arabic, ...). Layer 2 rejects Latin-script translations: distinctive diacritic
# characters of West/South-European languages (de/fr/es/it/pt/ro/tr) are rare in
# English prose, so a document whose ratio of lowercase diacritics to lowercase
# letters exceeds ``_DIACRITIC_RATIO`` is not English. Decided 2026-09-08
# (replaces the 16-word ``en_prose_words`` counter); ratio instead of an
# absolute count decided 2026-09-13: a long English README
# with a handful of accented proper nouns (a language-switch line "Español,
# Français, Türkçe", the word "Pokémon") is English, while a translation is
# dense with diacritics. Capitalized words (proper nouns, language names,
# sentence-initial German nouns) are ignored.
_NON_ENGLISH_DIACRITICS: frozenset[str] = frozenset("äöüßáéíóúñàâçèêëîïôûùœãõșțăîğışí")
# Diacritics per lowercase letter, in per-mille terms: 0.008 = 8 per 1000.
_DIACRITIC_RATIO = 0.008


def _strip_code_and_comments(text: str) -> str:
    """Keep only prose: drop HTML comments, code fences, inline code, URLs."""
    t = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"~~~.*?~~~", " ", t, flags=re.S)
    t = re.sub(r"`[^`]+`", " ", t)
    t = re.sub(r"https?://\S+", " ", t)
    return t


def is_english_document(text: str) -> bool:
    """Whether a document is (mostly) English prose.

    Non-Latin scripts (CJK, Cyrillic, Arabic, ...) fail on a script ratio.
    Latin-script translations (de/fr/es/it/pt/ro/tr) carry distinctive
    diacritics (``ä``, ``ñ``, ``ã``, ``ș``, ...) that are near-absent from
    English prose; a document whose ratio of *lowercase* diacritics to
    *lowercase* letters exceeds ``_DIACRITIC_RATIO`` (code, URLs and license
    boilerplate stripped, capitalized words ignored) is not English. Ignoring
    capitalized words keeps accented proper nouns and language-switch lines
    ("Español, Français, Türkçe", "Pokémon") from tripping the gate on an
    otherwise-English document.
    """
    body = _strip_code_and_comments(text)[:20000]
    letters = [ch for ch in body if ch.isalpha()]
    if not letters:
        return True
    non_latin = sum(1 for ch in letters if _NON_LATIN_RE.match(ch))
    if non_latin / len(letters) > 0.02:
        return False
    lower_letters = 0
    lower_diacritics = 0
    for word in re.findall(r"[^\W\d_]+", body):
        if word and word[0].isupper():
            continue  # proper noun / language name / capitalized word
        lower_letters += sum(1 for ch in word if ch.isalpha())
        lower_diacritics += sum(1 for ch in word if ch in _NON_ENGLISH_DIACRITICS)
    if lower_letters and lower_diacritics / lower_letters > _DIACRITIC_RATIO:
        return False
    return True


# Change-history documents are excluded from claim extraction: their entries are
# historical ("Added support for Python 3.7") rather than current-state claims,
# and DEPENDENCY exact-version matching turns them into false REFUTED against
# the manifest. Migration/upgrade guides ("upgrading_to_X") are the same genre —
# their "old → new" tables document removed paths, not current existence.
# Cross-language SDK trees (java-sdk/, go-sdk/, ts-sdk/) and ADR dirs describe
# non-Python APIs that the Python AST world cannot verify. Narrow-later moves
# grounded in the corpus runs.
_EXCLUDED_DOC_STEMS: frozenset[str] = load_list("pipeline.json", "excluded_doc_stems")

# Migration/upgrade guide paths (data/pipeline.json): a "migrate-from-X-to-Y"
# or "upgrade-guide" document is the same genre as the "migrating"/"upgrading"
# stems above, but the guide name is a phrase, not an exact stem. Kept as
# substrings so ``how-to/migrate-from-pydantic-v1-to-pydantic-v2.md`` is
# excluded while ordinary current-reference docs stay scanned.
_EXCLUDED_DOC_PATH_MARKERS: frozenset[str] = load_list(
    "pipeline.json", "excluded_doc_path_markers"
)


def _is_excluded_doc(rel_path: str) -> bool:
    if Path(rel_path).stem.lower() in _EXCLUDED_DOC_STEMS:
        return True
    low = rel_path.lower()
    for marker in (
        *_EXCLUDED_DOC_PATH_MARKERS,
        "release/",
        "releases/",
        "release-notes/",
        "release_notes/",
        "releasenotes/",
        "whats-new/",
        "whats_new/",
        "whatsnew/",
        "version-history",
        "changelog",
        "whats_new",
        "whatsnew",
        "history/",
        "older_versions",
        "updating",
        "upgrading",
        "/adr/",
        "java-sdk/",
        "go-sdk/",
        "ts-sdk/",
    ):
        if marker in low:
            return True
    stem = Path(rel_path).stem.lower()
    # Change-history file stems in any layout: ``0.19.0-notes.rst``,
    # ``v2-3-release-notes.md``, ``news_1.2.rst``, ``release-history.rst``.
    if (
        stem.endswith("-notes")
        or stem.endswith("_notes")
        or stem.endswith("-releasenotes")
        or stem.endswith("-release-notes")
        or stem.endswith("-release_notes")
        or stem.endswith("-history")
    ):
        return True
    return False


# Proposal/plan documents are not current-state descriptions: PEP-like
# proposals (pandas ``pdeps/``), planning docs (prefect ``plans/``), roadmap
# and ADR dirs describe intended, historical or decided-but-not-shipped states.
# Their claims must not refute against the manifest/listing (the abstention
# rules E:GENRE-PLAN). Unlike change-history documents these are
# still *extracted* — a proposal is readable prose — but a REFUTED verdict
# whose only refuting claims come from a plan document is downgraded to NEI.
_GENRE_PLAN_MARKERS: tuple[str, ...] = (
    "pdeps/",
    "plans/",
    "proposals/",
    "/roadmap/",
    "neps/",
    "sep/",
    "peps/",
    "rfcs/",
    "announce/",
    "enhancement-proposals/",
)


def _is_genre_plan_doc(source: str) -> bool:
    """Whether a document is a proposal/plan/announcement genre (not current-state)."""
    low = source.lower()
    return any(m in low for m in _GENRE_PLAN_MARKERS)


# Proposal/status documents carry a status header ("Status: Draft / Accepted /
# Final / Rejected"). Such documents describe decided-but-not-shipped or
# historical states, so their claims must not refute against the inventory.
# The path markers cover PEP-like directories; the header catches proposal
# files in any layout.
_STATUS_HEADER_RE = re.compile(
    r"^status\s*:\s*(draft|proposed|accepted|final|rejected|withdrawn|active)\b",
    re.IGNORECASE | re.MULTILINE,
)


def _is_status_header_doc(text: str) -> bool:
    return _STATUS_HEADER_RE.search(text) is not None


def _is_release_notes_document(text: str) -> bool:
    """Whether the document is a change-history/release-notes genre, not a
    current-state description. Release notes document past states ("requires
    Python 2.7"), so their claims must not adjudicate against the manifest.

    Detects the genre by a *top-level* heading: a level-1 Markdown heading
    (``# Release Notes``) or a reST title line with an underline. Section-level
    headings ("``## News``", "``## What's New``") do NOT make the whole document
    a release-notes doc — a README with a News section is current-state and
    must be scanned.
    """
    lines = text[:2000].splitlines()
    for i, line in enumerate(lines):
        low = line.strip().lower()
        if not low:
            continue
        if re.match(r"^#\s+(release notes|what'?s new|changelog|news)\b", low):
            return True
        if i + 1 < len(lines) and re.fullmatch(r"[=\-~^]+", lines[i + 1].strip()):
            if re.match(r"(release notes|what'?s new|changelog)\b", low):
                return True
            if "release" in low and re.search(r"\d+\.\d+", low):
                return True
    return False


@dataclass(slots=True)
class AnalysisResult:
    project_root: str
    scanned_documents: int = 0
    claims: list[PredicateClaim] = field(default_factory=list)
    referents: list[ReferentResult] = field(default_factory=list)
    evidence: list = field(default_factory=list)
    # Non-claims by construction (Phase 2 claim-gate): ``(predicate, reason,
    # object)`` triples that were excluded before the verdict layer. Kept for
    # transparency and calibration, not emitted as verdicts.
    gated_claims: list[tuple[str, str, str]] = field(default_factory=list)


_MANIFEST_NAMES: frozenset[str] = load_list("pipeline.json", "manifest_names")

# Live-progress callback: ``(kind, message)`` where ``kind`` is a coarse log
# tone — ``cmd`` / ``ok`` / ``info`` / ``step`` / ``pulse`` — that the web UI
# renders with a matching glyph. The pipeline emits real stage lines as it
# harvests inventories, scans documents and adjudicates assertions; the CLI and
# tests ignore the callback entirely (default ``None``).
ProgressFn = Callable[[str, str], None]

# Human description of what each predicate harvest does, keyed by predicate name.
# Used for the progress feed; a missing entry falls back to the world label.
_PREDICATE_ACTIONS: dict[str, str] = {
    "DEPENDENCY": "reading manifest declarations",
    "PATH_EXISTS": "indexing project file tree",
    "SYMBOL_EXISTS": "building AST symbol inventory",
    "LICENSE": "reading license metadata",
    "HAS_DOCKERFILE": "checking for a Dockerfile",
    "HAS_CI_WORKFLOW": "scanning CI workflows",
}


def _noop_progress(_kind: str, _message: str) -> None:
    pass


def exclusion_progress(_kind: str, message: str) -> None:
    """Progress sink that prints document/claim exclusion notices to stderr.

    ``analyze`` and ``dump`` otherwise never say which documents the language,
    change-history and release-notes gates dropped; the pipeline already emits
    those lines, so the CLI just needs a sink.
    """
    if "excluded" in message:
        print(message, file=sys.stderr)


def stamp_domain(item, domain_for) -> tuple[object, str]:
    """Stamp ``domain`` onto an evidence item; return ``(item, domain)``.

    The predicate contract does not require evidence to carry a ``domain``
    field (custom predicates may omit it). Only dataclasses with the field are
    replaced; the rest are grouped under the root domain.
    """
    if "domain" in {f.name for f in dataclasses.fields(item)}:
        domain = domain_for(item.source_file)
        return dataclasses.replace(item, domain=domain), domain
    return item, ""


def _has_manifest(path: Path) -> bool:
    return any((path / name).is_file() for name in _MANIFEST_NAMES) or any(
        p.is_file() and p.name.startswith("requirements") and p.name.endswith(".txt")
        for p in path.iterdir()
    )


def _looks_like_repo_root(path: Path) -> bool:
    """Whether a directory is (or contains) the repository's code root."""
    if _has_manifest(path):
        return True
    if any((path / name).is_dir() for name in ("src", "lib", "libs")):
        return True
    return any(p.suffix == ".py" for p in path.iterdir()) or any(
        p.is_dir() and (p / "__init__.py").is_file() for p in path.iterdir()
    )


def find_project_root(path: Path) -> Path:
    """Resolve an arbitrary passed path to the repository/code root.

    The given directory wins when it looks like a repo root (a manifest, a
    ``src``/``lib``/``libs`` layout, or importable Python directly). Otherwise,
    when exactly one immediate child looks like a repo root, descend into it —
    this is what makes corpus checkouts wrapped in a single ``source/``
    directory resolve without passing the inner path. Ambiguous trees stay as
    passed (the structure world guard then abstains instead of refuting).
    """
    current = path
    for _ in range(3):
        if _looks_like_repo_root(current):
            return current
        entries = [c for c in current.iterdir() if not c.name.startswith(".")]
        children = [c for c in entries if c.is_dir()]
        qualifying = [c for c in children if _looks_like_repo_root(c)]
        if len(qualifying) == 1:
            current = qualifying[0]
            continue
        # A pure wrapper (one directory, no files) is not itself a repository,
        # but it is not the project root either: descend so an upload of a
        # parent folder (``Project/checkout/...``) resolves to the checkout.
        if len(children) == 1 and not any(not c.is_dir() for c in entries):
            current = children[0]
            continue
        return current
    return current


def collect_documents(
    project_root: Path,
    *,
    progress: ProgressFn | None = None,
) -> list[tuple[str, str]]:
    """Every documentation file in the tree as ``(relative_path, text)``.

    In a git checkout the document set is the tracked snapshot
    (``git ls-files``) with NO ``SKIPPED_DIRS`` filter: a tracked ``doc/build/``
    or ``sites/`` tree is real documentation and must be scanned (sqlalchemy's
    202 files under ``doc/build/`` and paramiko's ``sites/`` were previously
    dropped). Git-less trees fall back to the working-tree walk
    with ``SKIPPED_DIRS`` and dot-dirs pruned.
    """
    emit = progress or _noop_progress
    emit("info", "scanning documentation tree…")
    documents: list[tuple[str, str]] = []
    history_excluded = 0
    non_english_excluded = 0
    release_notes_excluded = 0
    tracked = git_tracked_files(project_root)

    def _pruned_dirs(dirnames: list[str]) -> list[str]:
        return sorted(d for d in dirnames if d not in SKIPPED_DIRS and not d.startswith("."))

    if tracked is not None:
        for rel in sorted(tracked):
            if rel.startswith(".") or rel.startswith("/"):
                continue
            if not rel.endswith(tuple(_DOC_EXTENSIONS)):
                continue
            if _is_excluded_doc(rel):
                history_excluded += 1
                continue
            path = project_root / rel
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if not is_english_document(text):
                non_english_excluded += 1
                continue
            if _is_release_notes_document(text):
                release_notes_excluded += 1
                continue
            documents.append((rel, text))
    else:
        for dirpath, dirnames, filenames in Path(project_root).walk():
            dirnames[:] = _pruned_dirs(dirnames)
            rel_dir = dirpath.relative_to(project_root)
            base = "" if rel_dir == Path(".") else rel_dir.as_posix() + "/"
            for filename in sorted(filenames):
                if filename.startswith("."):
                    continue
                if not filename.endswith(tuple(_DOC_EXTENSIONS)):
                    continue
                rel = base + filename
                if _is_excluded_doc(rel):
                    history_excluded += 1
                    continue
                try:
                    text = (dirpath / filename).read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if not is_english_document(text):
                    non_english_excluded += 1
                    continue
                if _is_release_notes_document(text):
                    release_notes_excluded += 1
                    continue
                documents.append((rel, text))
    if history_excluded:
        emit("ok", f"excluded {history_excluded} change-history doc(s)")
    if non_english_excluded:
        emit("ok", f"excluded {non_english_excluded} non-English doc(s)")
    if release_notes_excluded:
        emit("ok", f"excluded {release_notes_excluded} release-notes doc(s)")
    emit("ok", f"{len(documents)} documentation file(s)")
    return documents


def analyze_repository(
    project_root: Path,
    plugins: Sequence[Predicate] = ALL_PREDICATES,
    *,
    documents: list[tuple[str, str]] | None = None,
    progress: ProgressFn | None = None,
) -> AnalysisResult:
    """Run the full claim analysis over the registered predicates (§4→§6→§7).

    Each plugin harvests its evidence inventory, scans every documentation file
    with its extractor, then its assertions are adjudicated against its own
    inventory. Claims from different predicates stay separate through
    ``predicate_type`` in the referent key. The project root is resolved first
    (``find_project_root``) so a wrapper directory (``source/``) resolves to the
    code root before harvests and doc collection. Every claim and evidence item
    is stamped with its domain: the manifest-bearing directory that
    contains its file, so monorepo sub-projects never mix in one referent.

    ``progress`` receives ``(kind, message)`` stage lines as the pipeline runs;
    it defaults to a no-op and never influences the result.
    """
    emit = progress or _noop_progress
    emit("cmd", "docassay analyze")
    clear_listing_cache()
    emit("info", "resolving project root…")
    root = find_project_root(project_root)
    emit("ok", f"project root: {root}")
    docs = documents if documents is not None else collect_documents(root, progress=emit)
    emit("info", "building domain index…")
    domains = DomainIndex.build(root)
    emit("ok", "domain index ready")

    by_name = {plugin.name: plugin for plugin in plugins}
    evidence_by_predicate: dict[str, dict[str, list]] = {}
    evidence_by_domain: dict[str, dict[str, dict[str, list]]] = defaultdict(dict)
    evidence_id_sources: dict[str, dict[str, str]] = {}
    all_evidence: list = []
    claims: list[PredicateClaim] = []
    scan_kwargs_by_predicate: dict[str, dict] = {}

    emit("step", "harvesting fact inventories")
    for plugin in plugins:
        action = _PREDICATE_ACTIONS.get(plugin.name, f"harvesting the {plugin.world} world")
        emit("info", f"{plugin.name} · {action}…")
        inventory = []
        domain_grouped: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        for item in plugin.harvest(root):
            stamped, domain = stamp_domain(item, domains.domain_for)
            inventory.append(stamped)
            domain_grouped[domain][item.object].append(stamped)
        all_evidence.extend(inventory)
        grouped: dict[str, list] = defaultdict(list)
        for item in inventory:
            grouped[item.object].append(item)
        evidence_by_predicate[plugin.name] = grouped
        evidence_by_domain[plugin.name] = domain_grouped
        evidence_id_sources[plugin.name] = {
            item.evidence_id: getattr(item, "source_file", "") for item in inventory
        }
        emit("ok", f"{plugin.name}: {len(inventory)} fact(s)")
        # The DEPENDENCY predicate's anchor set is extended at runtime with the
        # project's own manifest declarations, so any dependency the tool
        # harvests is always anchorable. Other predicates ignore
        # ``extra_names`` and use their fixed vocabulary.
        scan_kwargs = {}
        if plugin.extend_with_declared:
            extra_names = {
                getattr(item, "object", "") for item in inventory if plugin.anchor_evidence(item)
            }
            scan_kwargs["extra_names"] = frozenset(n for n in extra_names if n)
        if plugin.name == "SYMBOL_EXISTS":
            # Document-local module context (trial rule): the scan can qualify
            # a bare member name with the module a heading/table row/prose
            # lead-in names. Only the module inventory is passed; the symbol
            # names stay in the match layer.
            modules = {
                getattr(item, "qualified_name", "")
                for item in inventory
                if getattr(item, "kind", None) == KIND_MODULE
            }
            scan_kwargs["project_modules"] = frozenset(name.lower() for name in modules if name)
            scan_kwargs["top_packages"] = frozenset(
                name.split(".", 1)[0] for name in modules if name
            )
        scan_kwargs_by_predicate[plugin.name] = scan_kwargs

    emit("step", "extracting claims")
    gated_claims: list[tuple[str, str, str]] = []
    for plugin in plugins:
        emit("info", f"{plugin.name} · scanning {len(docs)} document(s)…")
        before = len(claims)
        for rel, text in docs:
            for c in plugin.scan(text, rel, **scan_kwargs_by_predicate[plugin.name]):
                c = dataclasses.replace(c, domain=domains.domain_for(rel))
                gate = plugin.gate(c)
                if gate.ok:
                    claims.append(c)
                else:
                    # Non-claim by construction (Phase 2 claim-gate): excluded
                    # before the verdict layer — like the §1 non-extraction
                    # exclusions, it never forms a referent/assertion.
                    gated_claims.append((plugin.name, gate.reason, c.object))
        emit("ok", f"{plugin.name}: {len(claims) - before} claim(s)")
    emit("info", f"{len(gated_claims)} non-claim(s) excluded by the claim-gate")

    emit("info", "grouping claims into assertions…")
    referents = group_into_assertions(claims)
    emit("ok", f"{len(claims)} claim(s) → {len(referents)} referent(s)")

    # Proposal/plan/announcement documents (path marker OR a "Status:" header):
    # their claims describe decided-but-not-shipped or historical states, so a
    # would-be REFUTED that is grounded only there is downgraded to NEI (REPORT
    # P9; the abstention rules E:GENRE-PLAN).
    genre_sources = frozenset(
        rel for rel, text in docs if _is_genre_plan_doc(rel) or _is_status_header_doc(text)
    )

    emit("step", "adjudicating assertions against the closed-world inventory")
    # ``world_holds`` depends only on (predicate, root), but its implementations
    # walk the whole tree (symbol fingerprint / manifest / license scans). Calling
    # it per referent made adjudication O(referents × tree size); evaluate it once
    # per predicate instead.
    world_holds_by_predicate = {plugin.name: plugin.world_holds(root) for plugin in plugins}
    total_referents = len(referents)
    adjudicated_list: list[ReferentResult] = []
    for done, referent in enumerate(referents, start=1):
        plugin = by_name[referent.predicate_type]
        adjudicated_list.append(
            _adjudicate(
                referent,
                plugin,
                evidence_by_predicate[referent.predicate_type],
                evidence_by_domain[referent.predicate_type],
                evidence_id_sources[referent.predicate_type],
                world_holds_by_predicate[referent.predicate_type],
                genre_sources,
            )
        )
        # Keep the stage observable on large repositories: without this a slow
        # adjudication looks like a hang between the step and completion lines.
        if done % 500 == 0 and done < total_referents:
            emit("info", f"adjudicated {done}/{total_referents} referent(s)…")
    adjudicated = tuple(adjudicated_list)
    emit("ok", "adjudication complete")
    clear_window_cache()

    return AnalysisResult(
        project_root=str(root),
        scanned_documents=len(docs),
        claims=claims,
        referents=adjudicated,
        evidence=all_evidence,
        gated_claims=gated_claims,
    )


def _adjudicate(
    referent: ReferentResult,
    plugin: Predicate,
    evidence_by_name: dict[str, list],
    evidence_by_domain: dict[str, dict[str, list]],
    evidence_id_sources: dict[str, str],
    world_holds: bool,
    genre_sources: frozenset[str],
) -> ReferentResult:
    adjudicated: list[Assertion] = []
    # A domain-scoped predicate (DEPENDENCY) adjudicates a sub-project claim
    # against that domain's own manifest only; a root-domain claim describes
    # the whole repository and sees the union of every manifest.
    # Whole-tree predicates (listing, project AST) always match the merged
    # inventory: their CLOSED worlds are over the entire tree.
    scoped = plugin.domain_scoped_evidence and referent.domain != ""
    scope = evidence_by_domain.get(referent.domain, {}) if scoped else evidence_by_name
    for assertion in referent.assertions:
        adjudicated.append(
            _adjudicate_assertion(
                assertion, plugin, scope, evidence_id_sources, world_holds, genre_sources
            )
        )
    return dataclasses.replace(referent, assertions=tuple(adjudicated))


def _adjudicate_assertion(
    assertion: Assertion,
    plugin: Predicate,
    evidence_by_name: dict[str, list],
    evidence_id_sources: dict[str, str],
    world_holds: bool,
    genre_sources: frozenset[str],
) -> Assertion:
    """Adjudicate one context-cluster of claims.

    Verdict: REFUTED wins — any REFUTED claim in the cluster refutes the whole
    assertion, and ``code_conflicts`` lists the refuting claim ids. The cluster
    is already homogeneous (claims were split by polarity and version in
    ``group_into_assertions``), so a REFUTED here is a genuine contradiction,
    not a cross-polarity accident. ``evidence_sources`` is derived from the
    *resolved* evidence actually used (supporting/refuting ids), so doc-relative
    and basename-resolved paths surface their source files.
    """
    if not world_holds:
        # The CLOSED world does not hold (no importable code / incomplete
        # inventory), so absence must not refute: abstain on every assertion.
        return dataclasses.replace(
            assertion,
            is_code_verifiable=False,
            code_verdict="NEI",
            code_verdict_layer="WORLD",
            code_verdict_reason="inventory incomplete",
        )
    per_claim = [
        (
            claim,
            plugin.match(claim.object, claim.context, evidence_by_name, **plugin.flags(claim)),
        )
        for claim in assertion.claims
    ]
    # A refuting claim from a proposal/plan document (pdeps/, plans/, roadmap/,
    # neps/, sep/, peps/, announce/, a "Status:"-headed proposal) describes an
    # intended or historical state, not the current repository, so it must never
    # refute on its own (the abstention rules E:GENRE-PLAN. The gate
    # is per-*claim* (not per-assertion): a genre claim cannot refute even when
    # it shares a context-cluster with a non-genre claim, and a real finding
    # stays REFUTED whenever a non-genre claim refutes.
    refuted = [
        claim
        for claim, verdict in per_claim
        if verdict.outcome == "REFUTED" and claim.source not in genre_sources
    ]
    genre_refuted = any(
        verdict.outcome == "REFUTED" and claim.source in genre_sources
        for claim, verdict in per_claim
    )
    supported = [claim for claim, verdict in per_claim if verdict.outcome == "SUPPORTED"]
    # The first NEI's layer/reason, if the assertion ends up NEI. Distinct
    # per-claim reasons stay visible in the raw claim dump.
    nei_reason = next(
        (v for _, v in per_claim if v.outcome == "NEI"),
        None,
    )

    if refuted:
        verdict = "REFUTED"
        conflicts = tuple(c.claim_id for c in refuted)
        refuting = tuple(
            sorted({eid for _, v in per_claim if v.outcome == "REFUTED" for eid in v.refuting})
        )
        supporting = ()
    elif genre_refuted:
        verdict = "NEI"
        conflicts = ()
        refuting = ()
        supporting = ()
        nei_reason = Verdict(
            "NEI", layer="CLAIM_GATE", reason="refutation grounded only in plan/proposal documents"
        )
    elif supported:
        verdict = "SUPPORTED"
        conflicts = ()
        supporting = tuple(sorted({eid for _, v in per_claim for eid in v.supporting}))
        refuting = ()
    else:
        verdict = "NEI"
        conflicts = ()
        supporting = ()
        refuting = ()

    layer = nei_reason.layer if (verdict == "NEI" and nei_reason is not None) else ""
    reason = nei_reason.reason if (verdict == "NEI" and nei_reason is not None) else ""
    if verdict == "REFUTED":
        # A resolved verdict carries no layer; its reason is an optional hint.
        reason = next(
            (
                v.reason
                for c, v in per_claim
                if v.outcome == "REFUTED" and c.source not in genre_sources and v.reason
            ),
            "",
        )
    elif verdict == "SUPPORTED":
        reason = next((v.reason for _, v in per_claim if v.outcome == "SUPPORTED" and v.reason), "")
    used_ids = supporting + refuting
    sources = tuple(
        sorted({source for eid in used_ids if (source := evidence_id_sources.get(eid, ""))})
    )
    return dataclasses.replace(
        assertion,
        evidence_sources=sources,
        is_code_verifiable=True,
        code_verdict=verdict,
        code_verdict_layer=layer,
        code_verdict_reason=reason,
        code_conflicts=conflicts,
        supporting_evidence=supporting,
        refuting_evidence=refuting,
    )
