"""The PATH_EXISTS predicate.

Extraction is anchor-first over backtick-quoted, path-shaped tokens (`` `setup.py` ``,
`` `src/pkg/mod.py` ``, `` `docs/` ``, "the `tests` directory"). The anchor is
syntactic, not a closed allowlist: any code token that looks like a file or
directory path can anchor a claim. Matching is presence against the project
file/directory listing — a unified inventory where directory keys keep a
trailing slash (``docs/``) so files (``docs``, ``docs/index.md``) and
directories never collide in one referent.

World (closed-over-listing): the listing is complete by construction, so a
claim about a path that is not in the listing is REFUTED — the CLOSED world
turns stale doc references into findings. A negation against an absent path is
NEI (§6.1, conservative). Historical mentions ("the previous `config.py` was
removed") and generative instructions ("create a file called `x.py`") downgrade
a would-be REFUTED to NEI. So does an extensionless slash *file* mention
(``gzip/bz2``, ``apache/airflow``): without a file suffix the token is often an
enumeration of variants or an identifier, not a project path, so the CLOSED
world abstains instead of refuting it.
"""

from __future__ import annotations

import dataclasses
import posixpath
import re

from docassay.core.models import Context, PredicateClaim
from docassay.core.windows import anchor_line_text, iter_windows_preserve_code, line_at
from docassay.data import load_list, regex_alternation
from docassay.evidence.listing import PathEvidence, build_structure_inventory
from docassay.markers.context import extract_contexts
from docassay.predicates.base import (
    GateResult,
    Predicate,
    Verdict,
    case_hint,
    mention_gate_reason,
)
from docassay.predicates.negation import window_negation
from docassay.vocabularies.markers import NEGATION_WORDS, is_historical_mention
from docassay.vocabularies.structure import (
    BARE_FILE_NAMES,
    FILE_EXTENSIONS,
    basename_candidates,
    directory_segments,
    has_placeholder_segment,
    is_dot_fragment_name,
    is_extensionless_slash_path,
    is_external_software_name,
    is_generated_artifact_name,
    is_generated_mention,
    is_hidden_tool_dir,
    is_placeholder_path,
    is_reader_file_name,
    is_reader_space_mention,
    is_rejectable_path,
    is_sphinx_role_anchor,
    is_user_config_mention,
    normalize_path,
    resolve_evidence_key,
)

PATH_EXISTS_PREDICATE = "PATH_EXISTS"
PATH_EXISTS_WORLD = "closed-over-listing"

# A backtick-quoted token with no whitespace and no operator characters. The
# character class deliberately excludes spaces and ``>``/``=`` so inline code
# like `` `pip install django>=5.0` `` or `` `from x import y` `` never anchors.
_FILE_ANCHOR_RE = re.compile(r"`([A-Za-z0-9_./~-]+)`")

# `` `docs/` `` — a backtick token ending in a slash is a directory mention.
_DIR_SLASH_RE = re.compile(r"`([A-Za-z0-9_./~-]+/)`")
# "the `tests` directory" — a backtick token immediately before a directory noun.
_DIR_PHRASE_RE = re.compile(
    r"`([^`]+)`\s+"
    r"(?:director(?:y|ies)|folder(?:s)?|subdirector(?:y|ies)|subdir(?:s)?|dir(?:s)?)\b",
    re.IGNORECASE,
)

# A path tokenizes into several word tokens (`src/a.py` → src, a, py), so the
# shared verb-gated negation in ``markers.context`` cannot attach a negator to
# it. The listing predicate supplies its own existence cue; the window logic is
# shared via ``predicates.negation``.
_EXISTENCE_NEG_RE = re.compile(
    r"(?:is\s+not\s+present|does\s+not\s+exist|do\s+not\s+exist|did\s+not\s+exist|"
    r"is\s+not\s+found|was\s+not\s+found|is\s+absent|no\s+such\s+(?:file|directory))",
    re.IGNORECASE,
)

# Generative/imperative verbs make a mention an instruction ("create a file
# called X", "add X to the repo"), not a claim that X currently exists.
# (data/markers.json)
_GENERATIVE_RE = re.compile(
    r"\b(?:" + regex_alternation(load_list("markers.json", "generative_verbs")) + r")\b",
    re.IGNORECASE,
)

# Example markers ("e.g. `x`", "such as `x`", "like `x`") signal an
# illustrative mention. Bare "example(s)" is excluded — it is often the anchor
# word itself (``the `examples` directory``). (data/markers.json)
_EXEMPLARY_RE = re.compile(
    r"\b(?:"
    + regex_alternation(load_list("markers.json", "exemplary_phrases"), escape=False)
    + r")\b|like\s*[`]",
    re.IGNORECASE,
)


def _is_file_path(token: str) -> bool:
    """Whether the backtick token looks like a file reference."""
    if token.endswith("/"):
        return False  # a trailing-slash token is a directory mention
    if "/" in token:
        return True
    low = token.lower()
    if low in BARE_FILE_NAMES:
        return True
    if low in FILE_EXTENSIONS:
        return False  # a bare extension mention (`` `.sql` ``), not a file
    return low.endswith(tuple(sorted(FILE_EXTENSIONS, key=len, reverse=True)))


# --- Bare filenames in prose (dedicated case) ----------------------------------
#
# A file name mentioned *without* backticks or a directory component
# (``FEATURE-TO-ENDPOINT-MAPPING.md``, ``nav.json``) is a project-path mention
# the anchor-first extractor misses. It is a separate, deliberately strict case:
# the token must be a standalone ``name.ext`` (not a path fragment, not inside
# markdown/HTML/template syntax), and an *unresolved* bare name only REFUTES
# when the window carries a reference marker ("see X.md", "X.md row 10",
# "documented in X.md") — otherwise it abstains. That keeps the CLOSED-world
# finding capability (a genuinely stale bare reference) without turning every
# identifier that ends in a file extension (``Series.diff``) into a refutation.
_EXT_ALTERNATION = "|".join(
    re.escape(e.lstrip(".")) for e in sorted(FILE_EXTENSIONS, key=len, reverse=True)
)
_BARE_FILENAME_RE = re.compile(
    rf"(?<![\w/.\`-])([A-Za-z0-9_][A-Za-z0-9_-]*\.(?:{_EXT_ALTERNATION}))"
    rf"(?![A-Za-z0-9])(?!\.\w)"
)
# Markdown link targets, raw HTML, template expressions, URLs and hex colours are
# masked (with spaces, preserving offsets) before the bare-name scan.
_MASK_RE = re.compile(
    r"https?://\S+|mailto:\S+|\]\([^)]*\)|<[^>]*>|\{\{[^}]*\}\}|\{%[^%]*%\}|"
    r"#[0-9A-Fa-f]{3,8}\b"
)
# A reference frame that makes a missing bare filename a real claim about the
# repo's tree. Deliberately narrow — generic words ("file", "read") are excluded
# so they cannot match the filename's own stem or a bare code token; a bare name
# without a frame abstains.
_FILENAME_REFERENCE_RE = re.compile(
    r"\b(?:see(?:\s+also)?|refer(?:red|ence|s)?|row|appendix|per|"
    r"document(?:ed|ation)?|described?\s+in|listed\s+in)\b",
    re.IGNORECASE,
)


def _mask_non_path_syntax(text: str) -> str:
    """Blank out URLs, HTML, templates, link targets and hex colours."""
    return _MASK_RE.sub(lambda m: " " * (m.end() - m.start()), text)


# A Markdown link/image target ``](docs/guide.md)`` is an explicit reference:
# unlike a bare prose path it is deliberate, so it anchors. URLs, in-page
# anchors, absolute/home/glob targets are skipped here; the verdict gates in
# ``path_exists_match`` (top-level-directory-absent, placeholder, generated, …)
# still apply downstream, so a hostname-like or non-repo target abstains.
_MD_LINK_RE = re.compile(r"\]\(\s*<?([^)\s>]+)>?\s*\)")
# Inline code spans (single/double backticks) and fenced code are *examples*, not
# real links — mask them before the Markdown-link scan so a documented
# ``![alt](path/to/img.png)`` snippet never becomes a path claim.
_INLINE_CODE_RE = re.compile(r"``[^`]*``|`[^`\n]*`")


def _mask_inline_code(text: str) -> str:
    return _INLINE_CODE_RE.sub(lambda m: " " * (m.end() - m.start()), text)


def _md_link_path(token: str, source: str) -> str | None:
    """The project-relative path a Markdown link target names, or ``None``.

    A link target is document-relative (``../tutorial/x.md`` in
    ``docs/advanced/a.md`` → ``docs/tutorial/x.md``), so it is normalized
    against the referencing document's directory.
    """
    core = token.split("#", 1)[0].split("?", 1)[0]
    if not core or any(ch in core for ch in "*?<>{}|"):
        return None
    if "://" in core or core.startswith(("mailto:", "#", "//", "/", "~")):
        return None
    if ":" in core.split("/", 1)[0]:
        return None  # drive-letter or scheme-like first segment
    if not _is_file_path(core):
        return None
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), core))


# --- PATH_EXISTS ---------------------------------------------------------------


def path_exists_scan(text: str, source: str) -> list[PredicateClaim]:
    """Anchor-first scan of one document → PATH_EXISTS claims.

    File anchors (backtick path-shaped tokens) and directory anchors
    (trailing-slash tokens, "the `X` directory" noun phrases) both yield one
    claim keyed by the normalized path — directory keys keep the trailing slash.
    """
    claims: list[PredicateClaim] = []
    seen: set[tuple[str, str]] = set()

    for line_idx, (window, line_start, _line_end, line_map) in enumerate(
        iter_windows_preserve_code(text)
    ):
        # Anchor on the token content (past the backtick) so polarity/restriction
        # attachment in extract_contexts maps it to its word token.
        dir_starts: set[int] = set()
        anchors: list[tuple[int, int, str, str]] = []
        for m in _DIR_SLASH_RE.finditer(window):
            if is_sphinx_role_anchor(window, m.span(1)[0]) or is_rejectable_path(m.group(1)):
                continue
            dir_starts.add(m.span(1)[0])
            anchors.append((m.span(1)[0], m.span(1)[1], m.group(1), "dir"))
        for m in _DIR_PHRASE_RE.finditer(window):
            if is_sphinx_role_anchor(window, m.span(1)[0]) or is_rejectable_path(m.group(1) + "/"):
                continue
            dir_starts.add(m.span(1)[0])
            anchors.append((m.span(1)[0], m.span(1)[1], m.group(1) + "/", "dir"))
        for m in _FILE_ANCHOR_RE.finditer(window):
            token = m.group(1)
            if not _is_file_path(token):
                continue
            if m.span(1)[0] in dir_starts:
                continue  # the same token is already a directory mention
            if is_sphinx_role_anchor(window, m.span(1)[0]) or is_rejectable_path(token):
                continue
            anchors.append((m.span(1)[0], m.span(1)[1], token, "file"))
        for m in _MD_LINK_RE.finditer(_mask_inline_code(window)):
            core = _md_link_path(m.group(1), source)
            if core is None or is_rejectable_path(core):
                continue
            anchors.append((m.start(1), m.end(1), core, "md-link"))
        masked = _mask_non_path_syntax(window)
        for m in _BARE_FILENAME_RE.finditer(masked):
            token = window[m.span(1)[0]:m.span(1)[1]]
            if is_rejectable_path(token):
                continue
            anchors.append((m.span(1)[0], m.span(1)[1], token, "bare-filename"))
        if not anchors:
            continue
        contexts = extract_contexts(
            window,
            [(start, end, token) for start, end, token, _type in anchors],
            normalize=normalize_path,
            is_plausible=lambda name, num: False,
            line_map=line_map,
        )
        for start, end, token, anchor_type in anchors:
            object_name = normalize_path(token)
            dedupe_key = (anchor_line_text(window, line_map, start), object_name)
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            claim_context = contexts[start]
            if window_negation(window, start, _EXISTENCE_NEG_RE):
                claim_context = dataclasses.replace(
                    claim_context, polarity=claim_context.polarity | {"not"}
                )
            else:
                # A generic verb-gated negator ("will not use `x.py`") is a
                # *usage* statement, not an existence negation ("`x.py` does
                # not exist"). Only existence negations flip the PATH verdict.
                claim_context = dataclasses.replace(
                    claim_context, polarity=claim_context.polarity - NEGATION_WORDS
                )
            claims.append(
                PredicateClaim(
                    claim_id=f"{source}:{line_idx}:{start}",
                    source=source,
                    predicate_type=PATH_EXISTS_PREDICATE,
                    object=object_name,
                    raw_context=anchor_line_text(window, line_map, start),
                    context=claim_context,
                    anchor_type=anchor_type,
                    line_start=line_at(line_map, start, line_start),
                    line_end=line_at(line_map, end - 1, line_start),
                    raw_object=token,
                )
            )
    return claims


def path_exists_harvest(project_root) -> list[PathEvidence]:
    """The project file + directory listing as the evidence inventory."""
    return build_structure_inventory(project_root, kind="both")


def path_exists_flags(claim: PredicateClaim) -> dict[str, bool | str]:
    """Downgrade signals (plus the claim's ``source`` for path resolution)."""
    return {
        "historical": is_historical_mention(claim.context, claim.raw_context),
        "source": claim.source,
        "instructional": _sentence_initial_instruction(claim.raw_context, _GENERATIVE_RE),
        "exemplary": bool(_EXEMPLARY_RE.search(claim.raw_context)),
        "user_config": is_user_config_mention(claim.object, claim.raw_context),
        "reader_space": is_reader_space_mention(claim.raw_context),
        "reader_file": is_reader_file_name(claim.object),
        "generated": is_generated_mention(claim.raw_context),
        "file_role": ":file:" in claim.raw_context,
        "bare_filename": claim.anchor_type == "bare-filename",
        "filename_reference": bool(_FILENAME_REFERENCE_RE.search(claim.raw_context)),
        "raw_object": claim.raw_object,
    }


def path_exists_gate(claim: PredicateClaim) -> GateResult:
    """Whether a scan-produced path mention is a current-state claim.

    Non-claims by construction (Phase 2): historical / instructional /
    exemplary / user-runtime-config mentions (non-current-state construction)
    and placeholder / extensionless-slash anchors (ambiguous form). These are
    decided before the inventory — the inventory cannot turn an instruction or
    a template into an existence claim. The instructional signal is
    *sentence-initial* imperative ("Add a file called X"); a descriptive
    "the build uses `X`" stays a claim.
    """
    if is_historical_mention(claim.context, claim.raw_context):
        return GateResult(False, "historical mention")
    if _sentence_initial_instruction(claim.raw_context, _GENERATIVE_RE):
        return GateResult(False, "instructional mention")
    if _EXEMPLARY_RE.search(claim.raw_context):
        return GateResult(False, "exemplary mention")
    if is_user_config_mention(claim.object, claim.raw_context):
        return GateResult(False, "user/runtime-config mention")
    if is_placeholder_path(claim.object):
        return GateResult(False, "placeholder path")
    if is_extensionless_slash_path(claim.object):
        return GateResult(False, "extensionless slash anchor")
    return GateResult()


def _sentence_initial_instruction(raw_context: str, regex: re.Pattern) -> bool:
    """Whether an imperative verb opens the window ("Add a file called X")."""
    low = raw_context.lstrip(" \t\n\r\"'`([{")
    return regex.match(low) is not None


def path_exists_match(
    object: str,
    context: Context,
    evidence_by_name: dict[str, list[PathEvidence]],
    *,
    historical: bool = False,
    source: str = "",
    instructional: bool = False,
    exemplary: bool = False,
    user_config: bool = False,
    reader_space: bool = False,
    reader_file: bool = False,
    generated: bool = False,
    file_role: bool = False,
    bare_filename: bool = False,
    filename_reference: bool = False,
    raw_object: str = "",
) -> Verdict:
    """Presence verdict against the unified listing (§6.1, CLOSED world).

    positive+evidence → SUPPORTED · negative+evidence → REFUTED ·
    negative∅ → NEI · positive∅ → REFUTED. A bare name that exists somewhere
    in the tree (several instances, so basename-unique resolution could not
    pick one) is a true existence claim → SUPPORTED. An instruction ("create
    X"), an example ("e.g. X"), a user/runtime-config mention, like a
    historical one, is not a current existence claim and downgrades the
    would-be REFUTED to NEI. An extensionless slash *file* mention
    (``gzip/bz2``) is an unreliable anchor — an enumeration, not a project
    path — and also downgrades to NEI. A placeholder segment
    (``version-x.x.x/``) is a template, not a concrete path — NEI.

    A claim that resolves to a tree path (an exact key, a doc-relative name, or
    a segment suffix) is SUPPORTED: a spelling that differs only by letter case
    (``docs/guide.md`` → ``docs/Guide.md``) is treated as the same path, not as
    a finding. Documentation systematically folds the case of code identifiers
    (``pkg.mod.Parser`` → ``pkg.mod.parser``); flagging case-only differences
    produced repeated false REFUTED across a single file's mentions.

    A Sphinx ``:file:`` role naming a *bare* filename (``:file:`layout.html```)
    is a tutorial's example file and abstains; a slash-carrying ``:file:``
    (``:file:`requirements/default.txt```) is a repo-relative path claim and
    stays adjudicated.

    The claimed path is resolved to an inventory key first (repo-root,
    document-relative, then a path suffix) — see
    ``vocabularies.structure.resolve_evidence_key``.
    """
    key = resolve_evidence_key(object, source, evidence_by_name)
    evidence = evidence_by_name.get(key, []) if key is not None else []
    negative = bool(context.polarity & NEGATION_WORDS)

    if negative:
        if not evidence:
            return Verdict("NEI", layer="WORLD", reason="negation with no evidence")
        return Verdict("REFUTED", (), _evidence_ids(evidence))
    if evidence:
        # Case-only differences are not findings, but the reader is told.
        hint = case_hint(raw_object, [getattr(e, "raw_path", "") or e.path for e in evidence])
        return Verdict("SUPPORTED", _evidence_ids(evidence), reason=hint)
    if "/" not in object.rstrip("/"):
        candidates = basename_candidates(object, evidence_by_name)
        if candidates:
            ids = tuple(eid for k in candidates for eid in _evidence_ids(evidence_by_name[k]))
            return Verdict("SUPPORTED", ids)
    gate_reason = mention_gate_reason(
        historical=historical,
        instructional=instructional,
        exemplary=exemplary,
        user_config=user_config,
        reader_space=reader_space,
        reader_file=reader_file,
        generated=generated,
    )
    if gate_reason:
        return Verdict("NEI", layer="CLAIM_GATE", reason=gate_reason)
    if is_extensionless_slash_path(object):
        return Verdict("NEI", layer="CLAIM_GATE", reason="extensionless slash anchor")
    if is_placeholder_path(object) or has_placeholder_segment(object):
        return Verdict("NEI", layer="CLAIM_GATE", reason="placeholder path")
    if is_external_software_name(object):
        return Verdict("NEI", layer="CLAIM_GATE", reason="external software artifact")
    if is_generated_artifact_name(object):
        return Verdict("NEI", layer="CLAIM_GATE", reason="generated artifact")
    if is_dot_fragment_name(object):
        return Verdict("NEI", layer="CLAIM_GATE", reason="filename fragment pattern")
    if is_hidden_tool_dir(object):
        # A hidden/tool directory (``.venv/``, ``.git/``, ``.hg/``) is runtime
        # state, not a stale repo path. Real repo-tracked dot dirs (``.github``,
        # ``.cargo``) are not in the tool pool and stay adjudicated.
        return Verdict("NEI", layer="CLAIM_GATE", reason="hidden/tool entry")
    if file_role and "/" not in object.rstrip("/"):
        # A Sphinx ``:file:`` role that names a *bare* example filename
        # (``:file:`layout.html```, ``:file:`addmodule.c```) is a tutorial's
        # reader-space file, not a repo path claim. A slash-carrying ``:file:``
        # (``:file:`requirements/default.txt```) is a repo-relative reference and
        # stays adjudicated, so the cue does not hide real stale-path findings.
        return Verdict("NEI", layer="CLAIM_GATE", reason="reader-space :file: example file")
    o = object.rstrip("/")
    if "/" in o:
        head = o.split("/", 1)[0]
        if head not in directory_segments(evidence_by_name):
            # A missing path whose first segment is not any directory of the
            # listing is not a stale reference into the project tree: it names a
            # directory the repo never had, or a bare reader/template name. The
            # listing is complete, so this is not an inventory gap (WORLD): the
            # mention is not taken as a claim about this tree (CLAIM_GATE), and
            # it is never REFUTED.
            return Verdict(
                "NEI", layer="CLAIM_GATE", reason="top-level directory absent from repository"
            )
    elif "." not in o:
        # A bare extensionless name that did not resolve (``readme``,
        # ``requirements``, ``myproject``) is a reader-space mention, not a
        # stale repo path.
        return Verdict("NEI", layer="CLAIM_GATE", reason="extensionless bare name")
    if bare_filename and not filename_reference:
        # A bare filename that exists nowhere and carries no reference frame is
        # too weak to refute: the same shape is produced by identifiers ending
        # in a file extension (``Series.diff``), tutorial examples and passing
        # mentions. It abstains unless the window actually refers to the file.
        return Verdict("NEI", layer="CLAIM_GATE", reason="unreferenced bare filename")
    return Verdict("REFUTED")


def _evidence_ids(items: list[PathEvidence]) -> tuple[str, ...]:
    return tuple(e.evidence_id for e in items)


path_exists_predicate = Predicate(
    name=PATH_EXISTS_PREDICATE,
    world=PATH_EXISTS_WORLD,
    scan=path_exists_scan,
    harvest=path_exists_harvest,
    match=path_exists_match,
    flags=path_exists_flags,
    gate=path_exists_gate,
)
