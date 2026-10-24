"""The SYMBOL_EXISTS predicate: extraction and matching.

One predicate for every structural symbol of the project's own code — modules,
classes, functions, methods and fields. Extraction is anchor-first over
code-shaped tokens: a dotted name (`` `pkg.mod.Class` ``), a call (`` `name()` ``,
`` `obj.method()` ``) and noun-gated mentions ("the `parse` function", "the
`limit` field"). Call syntax and nouns are just anchor forms; the referent is a
symbol, not a symbol kind.

World (closed-over-project): the Python AST inventory is complete for the
project's own tree, so a claim about a project symbol that is not in the
inventory is REFUTED — but only a *qualified* (dotted) claim can refute. Bare
single-segment mentions (``issubclass()``, ``get_chat_model()``,
``n_estimators``) are ambiguous (parameter, builtin, instance or external
symbol) and abstain. A bare member name is qualified only when the document
itself supplies the module (a module heading, a table-row module column or a
prose lead-in); without that context it stays bare and abstains. A dotted claim
whose top segment is not a project-owned top-level package is a third-party
symbol (NEI); historical, generative-instruction and example mentions downgrade
a would-be REFUTED to NEI.
"""

from __future__ import annotations

import dataclasses
import keyword
import re

from docassay.core.models import Context, PredicateClaim
from docassay.core.windows import anchor_line_text, iter_windows_preserve_code, line_at
from docassay.data import load_list, regex_alternation
from docassay.evidence.symbols import (
    KIND_FUNCTION,
    KIND_MODULE,
    SymbolEvidence,
    build_symbol_inventory,
    has_project_python,
)
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
    is_builtin_symbol,
    is_rejectable_path,
    is_sphinx_role_anchor,
    last_segment_candidates,
    normalize_symbol,
    resolve_symbol_key,
    top_level_packages,
)

SYMBOL_EXISTS_PREDICATE = "SYMBOL_EXISTS"
SYMBOL_EXISTS_WORLD = "closed-over-project"

# An identifier segment starts with a letter/underscore, so dotted numeric
# tokens (`` `2.4.1` ``) and toolchain tokens never anchor a symbol claim.
_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"
_SYMBOL_TOKEN = rf"{_IDENT}(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
_DOTTED = rf"{_IDENT}(?:\.[A-Za-z_][A-Za-z0-9_]*)+"

# `` `parse()` `` / `` `obj.parse()` `` — a call is a function/method mention.
_CALL_RE = re.compile(rf"`({_SYMBOL_TOKEN})\s*\(\)`")
# `` `pkg.mod` `` / `` `pkg.mod.Class` `` — a dotted, slash-free token.
_DOTTED_RE = re.compile(rf"`({_DOTTED})`")

# Noun-gated mentions: "the `parse` function", "the `limit` field", "module `x`".
# (data/markers.json)
_SYMBOL_NOUNS = regex_alternation(load_list("markers.json", "symbol_nouns"))
_NOUN_AFTER_RE = re.compile(rf"`([^`]+)`\s+(?:{_SYMBOL_NOUNS})\b", re.IGNORECASE)
_NOUN_BEFORE_RE = re.compile(rf"\b(?:{_SYMBOL_NOUNS})\s+`([^`]+)`", re.IGNORECASE)

# A dotted token whose last segment is a host TLD (``pypi.org``) is a link
# target, not a project symbol. (data/structure.json; the full IANA root zone.)
# The scan does NOT filter these: whether `` `pypi.org` `` is a website or
# ``airflow.providers.common.io`` is a real module is decided at match time
# against the inventory (only an *unresolved* TLD-ending claim abstains).
_HOST_TLDS: frozenset[str] = load_list("structure.json", "host_tlds")

# A window that configures the project (``values.yaml``, ``--set``, an entrypoint
# group) mentions dotted values (``app.enabled``, ``service.policy``) that
# are not code symbols.
_CONFIG_VALUE_RE = re.compile(
    r"values\.ya?ml|--set\b|entrypoint group|entry point group|chart value", re.IGNORECASE
)

# Placeholder segments used in developer docs (``pkg.foo.bar.baz``,
# ``pkg.mymodule``): not references to real project symbols.
# (data/structure.json)
_PLACEHOLDER_SEGMENTS: frozenset[str] = load_list("structure.json", "placeholder_segments")

# A symbol token is a single word (`parse`) or several (`pkg.mod`), so the
# shared verb-gated negation in ``markers.context`` cannot attach a negator to
# a dotted one. The structure predicate supplies its own existence cue; the
# window logic is shared via ``predicates.negation``.
_EXISTENCE_NEG_RE = re.compile(
    r"(?:is\s+not\s+present|does\s+not\s+exist|do\s+not\s+exist|did\s+not\s+exist|"
    r"is\s+not\s+found|was\s+not\s+found|is\s+absent|no\s+such\s+symbol)",
    re.IGNORECASE,
)

# Generative/imperative verbs make a mention an instruction ("add a parse
# function", "install the `requests` package"), not a current existence claim.
# (data/markers.json)
_GENERATIVE_RE = re.compile(
    r"\b(?:" + regex_alternation(load_list("markers.json", "generative_verbs")) + r")\b",
    re.IGNORECASE,
)

# Example markers ("e.g. `x`", "such as `x`", "like `x`") signal an
# illustrative mention. (data/markers.json)
_EXEMPLARY_RE = re.compile(
    r"\b(?:"
    + regex_alternation(load_list("markers.json", "exemplary_phrases"), escape=False)
    + r")\b|like\s*[`]",
    re.IGNORECASE,
)

# An RST anchor-definition line (``.. _`pytest.detailed_failed_tests_usage`:``)
# is a cross-reference label, not a project symbol.
_RST_ANCHOR_RE = re.compile(r"^\.\.\s+_`[^`]+`:\s*$")

# A plugin entry-point group name ("the `commitizen.provider` entry point",
# "as a `poetry.application.plugin` plugin:") is a distribution metadata key,
# not a code symbol.
_ENTRY_POINT_RE = re.compile(r"\bentry\s+point\b|\bplugin\s*:", re.IGNORECASE)

# --- document-local module context (trial rule) --------------------------------
# Natural API-reference docs name a module once (a section heading, a table
# cell, a prose lead-in) and then mention its members by bare name
# (``### `Reading` ``, ``### `read_station_id() -> str` ``). Such a bare name
# cannot refute on its own — it may be a parameter, a return type or an
# instance attribute — so the scan qualifies it only when the document itself
# supplies the owning module. Qualification is supplied by the pipeline
# (``project_modules``); without it the scan keeps its historical behaviour, so
# bare names stay bare and never refute.
_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})\s+(\S.*)$")
_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_BACKTICK_TOKEN_RE = re.compile(r"`([^`\n]+)`")
_FENCE_LINE_RE = re.compile(r"^\s*(?:`{3,}|~{3,})")

# Kind words may prefix the documented name inside the backticks
# (``### `class Canvas` ``, ``### `def parse()` ``).
_KIND_PREFIX_RE = re.compile(
    r"^(?:class|def|function|method|property|attribute|constant)\s+", re.IGNORECASE
)
_SIGNATURE_RE = re.compile(rf"({_IDENT})\s*\([^)]*\)\s*(?:->\s*\S.*)?$")
_BARE_NAME_RE = re.compile(rf"({_IDENT})$")

# API-reference prose cues. A prose line is an anchor context only when it
# names a code artifact ("the module declares X", "the function returns X").
# The trigger is searched after removing backticked spans, so a symbol whose
# name happens to be a trigger word does not anchor itself.
_TRIGGER_RE = re.compile(
    r"\b(?:functions?|class(?:es)?|methods?|modules?|uses?|used|returns?|"
    r"calls?|called|imports?|attributes?|parameters?|constants?)\b",
    re.IGNORECASE,
)

# A declaration cue directly after a bare name ("`scale_quantity` returns",
# "`nice_ticks` ->") makes a list/prose mention a module member under a
# section heading. Attribute lists ("- `timestamp`: ...") have no such cue and
# stay bare, which keeps instance attributes from being qualified to the
# module namespace.
_RETURN_CUE_TEMPLATE = r"`?\b{name}\b`?\s*(?:\([^`)]*\))?\s*(?:->|returns?\b|returning\b)"

_MODULE_SOURCE_SUFFIXES = (".pyi", ".pyx", ".pxd", ".py")
_MODULE_IMPORT_ROOTS = frozenset({"src", "lib", "libs"})

# A usage/relationship verb between a module and a name does not assert
# membership: "``prefect._internal`` uses ``_SafeStreamHandler``" names a helper
# defined elsewhere. Declaration/location relations (declares, defines,
# provides, contains, "the `Color` class in `palette/colors.py`") do.
_USAGE_GAP_RE = re.compile(
    r"\b(?:uses?|used|using|calls?|called|calling|imports?|imported|importing|"
    r"returns?|returned|returning|passes?|passed|passing|takes?|took|accepts?|"
    r"receives?|wraps?|subclasses?|extends?)\b",
    re.IGNORECASE,
)


def _is_identifier_path(token: str) -> bool:
    return all(re.fullmatch(_IDENT, part) for part in token.split("."))


def _is_usable_symbol(window: str, start: int, token: str) -> bool:
    """Whether a symbol-shaped token is a claim about the project's own code.

    Rejects path tokens (`` `src/a.py` ``, `` `docs/` `` — those belong to the
    listing predicates), Sphinx cross-references, rejectable paths, bare
    extension/file-name mentions, non-identifier tokens (``*time.Time``,
    ``data-testid``, ``--source``), config/chart values in configuring windows
    and placeholder segments (``foo``/``bar``).
    """
    if "/" in token:
        return False
    if any(ch.isspace() for ch in token):
        return False
    if is_sphinx_role_anchor(window, start):
        return False
    if is_rejectable_path(token):
        return False
    low = token.lower()
    if low in BARE_FILE_NAMES:
        return False
    if low.endswith(tuple(sorted(FILE_EXTENSIONS, key=len, reverse=True))):
        return False
    if not _is_identifier_path(token):
        return False
    if _CONFIG_VALUE_RE.search(window):
        return False
    if _PLACEHOLDER_SEGMENTS.intersection(token.split(".")):
        return False
    return True


def _claims_for_anchors(
    window: str,
    line_idx: int,
    source: str,
    anchors: list[tuple[int, int, str, str]],
    line_start: int,
    line_map,
) -> list[PredicateClaim]:
    """Build one claim per anchor, with context and existence-negation."""
    if not anchors:
        return []
    contexts = extract_contexts(
        window,
        [(start, end, token) for start, end, token, _type in anchors],
        normalize=normalize_symbol,
        is_plausible=lambda name, num: False,
        line_map=line_map,
    )
    claims: list[PredicateClaim] = []
    seen: set[tuple[str, str]] = set()
    for start, end, token, anchor_type in anchors:
        object_name = normalize_symbol(token)
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
            # A generic verb-gated negator ("we are not using `x()`") is a
            # usage statement, not a symbol-existence negation.
            claim_context = dataclasses.replace(
                claim_context, polarity=claim_context.polarity - NEGATION_WORDS
            )
        claims.append(
            PredicateClaim(
                claim_id=f"{source}:{line_idx}:{start}",
                source=source,
                predicate_type=SYMBOL_EXISTS_PREDICATE,
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


def _bare_token_parts(body: str) -> tuple[str, str, int] | None:
    """``(name, anchor_type, offset)`` for a bare code-shaped token body.

    Accepts a plain identifier (``anchor_type="bare"``) and a call/signature
    (``name`` / ``name(...)`` / ``name() -> type``, ``anchor_type="signature"``)
    after stripping an optional kind prefix. Dotted names, paths, placeholders
    and non-identifier text return ``None``. ``offset`` is the name's position
    inside ``body`` so the caller can point the anchor at the name.
    """
    stripped = body.strip()
    lead = len(body) - len(body.lstrip())
    kind = _KIND_PREFIX_RE.match(stripped)
    if kind:
        stripped = stripped[kind.end() :]
        lead += kind.end()
    signature = _SIGNATURE_RE.fullmatch(stripped)
    if signature:
        return signature.group(1), "signature", lead + signature.start(1)
    bare = _BARE_NAME_RE.fullmatch(stripped)
    if bare:
        return bare.group(1), "bare", lead + bare.start(1)
    return None


def _is_usable_bare_name(window: str, start: int, name: str) -> bool:
    """Whether a bare name can anchor a claim at all.

    Builtins and Python keywords (``None``, ``True``, ``False``, ``str``,
    ``float``) are values/types, not project symbols; anchoring them would let
    a module context qualify them into a false finding.
    """
    if not _is_usable_symbol(window, start, name):
        return False
    if keyword.iskeyword(name):
        return False
    return not is_builtin_symbol(name.lower())


def _normalize_modules(project_modules) -> frozenset[str]:
    return frozenset(m.strip().lower() for m in project_modules or () if m and m.strip())


def _normalize_tops(top_packages, modules: frozenset[str]) -> frozenset[str]:
    if top_packages is None:
        return frozenset(m.split(".", 1)[0] for m in modules)
    return frozenset(t.strip().lower() for t in top_packages or () if t and t.strip())


def _module_for_token(token: str, modules: frozenset[str], tops: frozenset[str]) -> str | None:
    """The project module a document token names, spelled as the document does.

    A dotted module token (`` `gaugekit.loader` ``) is matched directly; a
    module *path* (`` `palette/harmony.py` ``, optionally under ``src/``) is
    mapped to its dotted import name and must resolve to a harvested module.
    Only project-owned modules qualify (the top package must be in ``tops``).
    """
    text = token.strip()
    if not text or any(ch.isspace() for ch in text):
        return None
    if text.startswith(("/", "~", "..")):
        return None
    while text.startswith("./"):
        text = text[2:]
    if not text:
        return None

    candidates: list[tuple[str, str]] = []
    if re.fullmatch(_DOTTED, text):
        candidates.append((text, text.lower()))

    path = text.replace("\\", "/")
    suffix = next((s for s in _MODULE_SOURCE_SUFFIXES if path.lower().endswith(s)), None)
    if suffix is not None:
        path = path[: -len(suffix)]
        parts = [part for part in path.split("/") if part and part != "."]
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        if parts:
            dotted = ".".join(parts)
            candidates.append((dotted, dotted.lower()))
            if parts[0].lower() in _MODULE_IMPORT_ROOTS and len(parts) > 1:
                dotted = ".".join(parts[1:])
                candidates.append((dotted, dotted.lower()))

    for spelled, low in candidates:
        if low in modules and low.split(".", 1)[0] in tops:
            return spelled
    return None


def _line_module(line: str, modules: frozenset[str], tops: frozenset[str]) -> str | None:
    """The unique project module named on a line (``None`` when ambiguous)."""
    found: list[str] = []
    for match in _BACKTICK_TOKEN_RE.finditer(line):
        module = _module_for_token(match.group(1), modules, tops)
        if module is not None and module not in found:
            found.append(module)
    return found[0] if len(found) == 1 else None


def _same_line_membership(line: str, module: str, name: str, modules, tops) -> bool:
    """Whether a module/name pair on one line reads as a membership statement.

    ``False`` when a usage verb sits between the two (``module uses Name``), so
    a helper defined in another module is not attributed to this one. Table
    rows bypass the check: their module column is a declared owner.
    """
    module_span: tuple[int, int] | None = None
    name_span: tuple[int, int] | None = None
    for match in _BACKTICK_TOKEN_RE.finditer(line):
        token = match.group(1)
        if module_span is None and _module_for_token(token, modules, tops) == module:
            module_span = match.span()
        if name_span is None:
            parts = _bare_token_parts(token)
            if parts is not None and parts[0] == name:
                name_span = match.span()
    if module_span is None or name_span is None:
        return True
    gap = (
        line[module_span[1] : name_span[0]]
        if name_span[0] >= module_span[1]
        else line[name_span[1] : module_span[0]]
    )
    return _USAGE_GAP_RE.search(gap) is None


def _fenced_lines(lines: list[str]) -> list[bool]:
    """1-based flags for lines inside fenced code blocks (fence lines included)."""
    fenced = [False] * (len(lines) + 1)
    inside = False
    for number, line in enumerate(lines, start=1):
        if _FENCE_LINE_RE.match(line):
            inside = not inside
            fenced[number] = True
        else:
            fenced[number] = inside
    return fenced


def _heading_module_contexts(
    lines: list[str],
    fenced: list[bool],
    modules: frozenset[str],
    tops: frozenset[str],
) -> list[str | None]:
    """Nearest preceding module-heading context per physical line.

    A heading whose (unique) backticked module token is a project module opens
    a section for that module; a later heading at the same or a higher level
    that does not name a module closes it. Nested symbol headings
    (``### `Reading` ``) inherit the surrounding module.
    """
    contexts: list[str | None] = [None] * (len(lines) + 1)
    current: str | None = None
    level: int | None = None
    for number, line in enumerate(lines, start=1):
        if not fenced[number]:
            heading = _HEADING_RE.match(line)
            if heading:
                heading_level = len(heading.group(1))
                module = _line_module(line, modules, tops)
                if module is not None:
                    current = module
                    level = heading_level
                elif current is not None and heading_level <= (level or 0):
                    current = None
                    level = None
        contexts[number] = current
    return contexts


def _anchor_line_kind(line: str) -> str | None:
    """The bare-anchor context a line supplies: heading, list item or trigger."""
    if _HEADING_RE.match(line):
        return "heading"
    if _LIST_ITEM_RE.match(line):
        return "list"
    if _TRIGGER_RE.search(_BACKTICK_TOKEN_RE.sub(" ", line)):
        return "trigger"
    return None


def _has_return_cue(line: str, name: str) -> bool:
    pattern = _RETURN_CUE_TEMPLATE.format(name=re.escape(name))
    return re.search(pattern, line) is not None


def _contextual_anchors(
    window: str,
    line_start: int,
    line_map,
    lines: list[str],
    fenced: list[bool],
    heading_contexts: list[str | None],
    modules: frozenset[str],
    tops: frozenset[str],
    existing_spans: set[tuple[int, int]],
) -> tuple[list[tuple[int, int, str, str]], dict[tuple[int, int], str]]:
    """Bare anchors from document context, plus their module qualifications.

    Selects the first bare code-shaped token on each physical line of the
    window (module tokens and builtins excluded), so only the documented
    subject anchors — not every later return type or attribute mention. A
    token is anchored when its line is a heading, a list item, a prose line
    with a code-artifact trigger, or a line that itself names a project module
    (table row / prose lead-in).

    Qualification applies when a same-line module is present, for heading
    anchors, for call/signature anchors, and for list/prose mentions directly
    followed by a return cue. A bare identifier in ordinary prose under a
    section heading stays bare (NEI): qualifying it would refute instance
    attributes and imported return types against the module namespace. A
    token already anchored by the historical call/noun forms is left as it was
    under a same-line module; under a heading it keeps its historical form
    when the line has no other anchor context.
    """
    selected: dict[int, tuple[int, int, str, str]] = {}
    for match in _BACKTICK_TOKEN_RE.finditer(window):
        parts = _bare_token_parts(match.group(1))
        if parts is None:
            continue
        name, anchor_type, offset = parts
        start = match.start(1) + offset
        end = start + len(name)
        if not _is_usable_bare_name(window, start, name):
            continue
        line_no = line_at(line_map, start, line_start)
        if line_no in selected:
            continue
        if 0 < line_no < len(fenced) and fenced[line_no]:
            continue
        selected[line_no] = (start, end, name, anchor_type)

    anchors: list[tuple[int, int, str, str]] = []
    qualifications: dict[tuple[int, int], str] = {}
    for line_no, (start, end, name, anchor_type) in selected.items():
        line = lines[line_no - 1] if 0 < line_no <= len(lines) else ""
        # The same-line context is the anchor's own sentence/line inside the
        # window, not the whole physical line: a long prose line is split into
        # sentence windows, and a module named in another sentence must not
        # qualify this one. Table-row windows are per-cell, so the row itself
        # supplies the module.
        segment = anchor_line_text(window, line_map, start)
        is_table = line.lstrip().startswith("|")
        context_text = line if is_table else segment
        line_module = _line_module(segment, modules, tops)
        if line_module is None and is_table:
            line_module = _line_module(line, modules, tops)
        heading_module = heading_contexts[line_no] if 0 < line_no < len(heading_contexts) else None
        kind = _anchor_line_kind(context_text)
        if kind is None and _LIST_ITEM_RE.match(line):
            kind = "list"
        already_anchored = (start, end) in existing_spans
        if not already_anchored:
            if line_module is None and kind is None:
                continue
            anchors.append((start, end, name, anchor_type))
        module = line_module or heading_module
        if module is None:
            continue
        if line_module is not None:
            # The same-line module qualifies the name it introduces; it does
            # not rewrite a pre-existing call/noun claim on that prose line,
            # and a usage relation ("module uses X") is not membership.
            if not already_anchored and (
                is_table or _same_line_membership(line, module, name, modules, tops)
            ):
                qualifications[(start, end)] = f"{module}.{name}"
            continue
        if (
            kind == "heading"
            or anchor_type in ("call", "signature")
            or _has_return_cue(context_text, name)
        ):
            qualifications[(start, end)] = f"{module}.{name}"
    return anchors, qualifications


def symbol_exists_scan(
    text: str,
    source: str,
    *,
    project_modules: frozenset[str] | set[str] | None = None,
    top_packages: frozenset[str] | set[str] | None = None,
) -> list[PredicateClaim]:
    """Anchor-first scan of one document → SYMBOL_EXISTS claims.

    ``project_modules`` (dotted module names from the AST inventory) enables
    document-local context qualification: the scan tracks the nearest module
    section heading and the module named on a line, and qualifies a bare
    member name with that module (``gaugekit.loader.read_station_id``). Without
    it — or without any document context — bare names stay bare and the match
    layer abstains on them (they can never REFUTE).
    """
    modules = _normalize_modules(project_modules) if project_modules is not None else None
    tops = _normalize_tops(top_packages, modules) if modules is not None else frozenset()
    lines = text.splitlines() if modules is not None else []
    fenced = _fenced_lines(lines) if modules is not None else []
    heading_contexts = (
        _heading_module_contexts(lines, fenced, modules, tops) if modules is not None else []
    )

    claims: list[PredicateClaim] = []
    for line_idx, (window, line_start, _line_end, line_map) in enumerate(
        iter_windows_preserve_code(text)
    ):
        anchors: list[tuple[int, int, str, str]] = []
        for m in _CALL_RE.finditer(window):
            token = m.group(1)
            if _is_usable_symbol(window, m.span(1)[0], token):
                anchors.append((m.span(1)[0], m.span(1)[1], token, "call"))
        for m in _DOTTED_RE.finditer(window):
            token = m.group(1)
            if _is_usable_symbol(window, m.span(1)[0], token):
                anchors.append((m.span(1)[0], m.span(1)[1], token, "dotted"))
        for m in _NOUN_AFTER_RE.finditer(window):
            token = m.group(1)
            if _is_usable_symbol(window, m.span(1)[0], token):
                anchors.append((m.span(1)[0], m.span(1)[1], token, "noun"))
        for m in _NOUN_BEFORE_RE.finditer(window):
            token = m.group(1)
            if _is_usable_symbol(window, m.span(1)[0], token):
                anchors.append((m.span(1)[0], m.span(1)[1], token, "noun"))
        if modules is not None:
            contextual, qualifications = _contextual_anchors(
                window,
                line_start,
                line_map,
                lines,
                fenced,
                heading_contexts,
                modules,
                tops,
                {(start, end) for start, end, _token, _type in anchors},
            )
            anchors.extend(contextual)
            anchors = [
                (start, end, qualifications.get((start, end), token), anchor_type)
                if "." not in token
                else (start, end, token, anchor_type)
                for start, end, token, anchor_type in anchors
            ]
        claims.extend(_claims_for_anchors(window, line_idx, source, anchors, line_start, line_map))
    return claims


def symbol_exists_flags(claim: PredicateClaim) -> dict[str, bool | str]:
    """Downgrade signals: historical, generative-instruction, example."""
    return {
        "historical": is_historical_mention(claim.context, claim.raw_context),
        "instructional": _sentence_initial_instruction(claim.raw_context, _GENERATIVE_RE),
        "exemplary": bool(_EXEMPLARY_RE.search(claim.raw_context)),
        "rst_anchor": bool(_RST_ANCHOR_RE.match(claim.raw_context.strip())),
        "entry_point": bool(_ENTRY_POINT_RE.search(claim.raw_context)),
        "raw_object": claim.raw_object,
    }


def symbol_exists_gate(claim: PredicateClaim) -> GateResult:
    """Whether a scan-produced symbol mention is a current-state claim.

    Non-claims by construction (Phase 2): historical / instructional /
    exemplary mentions (non-current-state construction). Evidence-dependent
    form cases (foreign top, unresolved bare name, host-TLD ending, Cython
    surface) stay in the verdict layer — they need the inventory to decide.
    A last-segment host TLD (``airflow.apache.org``, ``docs.sqlfluff.com``) is
    only a website mention when the name does NOT resolve against the
    inventory; the match layer already abstains on an unresolved TLD-ending
    claim, so gating it here drops real symbols whose last
    segment is an IANA TLD (``typer.run``, ``pytest.fail``, ``numpy.save``).

    The instructional signal is *sentence-initial* imperative ("Add a parse
    function") — a descriptive present-tense mention ("The module defines X")
    is exactly the current-state claim the predicate must adjudicate.
    """
    if is_historical_mention(claim.context, claim.raw_context):
        return GateResult(False, "historical mention")
    if _sentence_initial_instruction(claim.raw_context, _GENERATIVE_RE):
        return GateResult(False, "instructional mention")
    if _EXEMPLARY_RE.search(claim.raw_context):
        return GateResult(False, "exemplary mention")
    return GateResult()


def _sentence_initial_instruction(raw_context: str, regex: re.Pattern) -> bool:
    """Whether an imperative verb opens the window ("Add a CI workflow").

    ``regex.match`` is anchored at the start of the stripped window, so the
    directive must be the first content word — a descriptive "The module
    defines X" never matches.
    """
    low = raw_context.lstrip(" \t\n\r\"'`([{")
    return regex.match(low) is not None


def symbol_exists_match(
    object: str,
    context: Context,
    evidence_by_name: dict[str, list[SymbolEvidence]],
    *,
    historical: bool = False,
    instructional: bool = False,
    exemplary: bool = False,
    rst_anchor: bool = False,
    entry_point: bool = False,
    raw_object: str = "",
) -> Verdict:
    """Presence verdict against the symbol inventory (§6.1, CLOSED world).

    positive+evidence → SUPPORTED · negative+evidence → REFUTED ·
    negative∅ → NEI · positive∅ → REFUTED. A bare symbol name that exists
    somewhere in the tree (several instances, so suffix resolution could not
    pick one) is a true existence claim → SUPPORTED. Symbol names stay
    case-folded on purpose: docs routinely lowercase CamelCase classes
    (``pkg.mod.Parser`` → ``pkg.mod.parser``), so a *lowercase* doc name is not
    a finding. The asymmetry is kept for the class-vs-module confusion: a
    capitalized last segment (``mypkg.Client``) resolved only to a module whose
    own spelling is lowercase (``mypkg.client``) is REFUTED with a "did you
    mean" hint — the class the doc names does not exist.

    Conservative abstentions: a dotted claim whose top segment is not a
    project-owned top-level package is a third-party symbol (NEI); an
    unresolved bare mention (``issubclass``, ``get_chat_model()``,
    ``n_estimators``) is an instance/stdlib/external reference, not an
    existence claim about a project symbol (NEI). A *negated* bare mention
    abstains even when its last segment resolves to some project symbol: the
    name is still ambiguous (parameter, instance attribute, re-export), so its
    negation is not a CLOSED-world contradiction. An instruction, an example
    or a historical mention downgrades the would-be REFUTED to NEI. A dotted
    claim into a Cython/generated surface (``cython_blas``, a module that
    exists only as ``.pyx``/``.pxd``/``.pyi``) abstains: the AST inventory
    cannot enumerate symbols there, so absence is not conclusive. The same
    holds for a **dynamic surface** — a module with a module-level
    ``__getattr__`` (PEP 562) or a known dynamically-constructed namespace
    (``pytest.mark``): attributes there are produced at runtime
    (``click.get_text_stream``, ``pytest.mark.parametrize``), so absence is not
    conclusive. A qualified claim whose *last* segment is a
    host TLD and that does not resolve is a website mention of the project's
    own domain (``airflow.apache.org``, ``docs.sqlfluff.com``), not an
    existence claim about a missing symbol — it abstains instead of REFUTING.
    """
    key = resolve_symbol_key(object, evidence_by_name)
    evidence = evidence_by_name.get(key, []) if key is not None else []
    negative = bool(context.polarity & NEGATION_WORDS)

    if rst_anchor or entry_point:
        # An RST cross-reference label or a plugin entry-point group name is a
        # documentation/meta symbol, not a project code symbol.
        return Verdict("NEI", layer="CLAIM_GATE", reason="non-symbol mention")

    if (
        "." in object
        and object.split(".", 1)[0] not in top_level_packages(evidence_by_name)
        and not (key is not None and key.endswith("." + object))
    ):
        # A dotted claim into a third-party package is never a project symbol.
        # The guard runs before evidence lookup and only when the resolution is
        # a bare last-segment match (the claim is not a suffix of the resolved
        # key): ``logging.debug`` must not match ``mlflow.…debug``. A suffix
        # match (``basehook.get_connection`` → ``airflow.…basehook
        # .get_connection``) is a legitimate shortened reference and stays.
        return Verdict("NEI", layer="WORLD", reason="foreign top segment")

    if negative:
        if not evidence:
            return Verdict("NEI", layer="WORLD", reason="negation with no evidence")
        if "." not in object:
            # A bare name is ambiguous even when it resolves to *some* symbol
            # (a parameter, an instance attribute, a type alias); a negation of
            # it is not a CLOSED-world contradiction (the scope document §3.3.1).
            return Verdict("NEI", layer="CLAIM_GATE", reason="negated bare name")
        return Verdict("REFUTED", (), _evidence_ids(evidence))
    if evidence:
        mismatch = _class_vs_module_spelling(object, raw_object, evidence, evidence_by_name)
        if mismatch is not None and not (historical or instructional or exemplary):
            return Verdict(
                "REFUTED",
                (),
                _evidence_ids(evidence),
                reason=f"class/attribute name matches only a module (did you mean: {mismatch})",
            )
        hint = case_hint(raw_object, [e.qualified_name for e in evidence], separators=".")
        return Verdict("SUPPORTED", _evidence_ids(evidence), reason=hint)

    if "." not in object:
        # A bare name is never a CLOSED finding: it could be a parameter, a
        # builtin or an external symbol. Resolved → SUPPORTED, else NEI.
        matches = last_segment_candidates(object, evidence_by_name)
        if matches:
            ids = tuple(eid for k in matches for eid in _evidence_ids(evidence_by_name[k]))
            return Verdict("SUPPORTED", ids)
        return Verdict("NEI", layer="CLAIM_GATE", reason="unresolved bare name")

    top = object.split(".")[0]
    project_top = top_level_packages(evidence_by_name)
    if top not in project_top:
        return Verdict("NEI", layer="WORLD", reason="top not in project packages")
    if historical or instructional or exemplary:
        reason = mention_gate_reason(
            historical=historical, instructional=instructional, exemplary=exemplary
        )
        return Verdict("NEI", layer="CLAIM_GATE", reason=reason)
    if _is_cython_generated(object, evidence_by_name):
        return Verdict("NEI", layer="CLAIM_GATE", reason="cython/generated surface")
    if _is_dynamic_surface(object, evidence_by_name):
        return Verdict("NEI", layer="CLAIM_GATE", reason="dynamic surface")
    last = object.rsplit(".", 1)[-1]
    if last in _HOST_TLDS:
        return Verdict(
            "NEI", layer="CLAIM_GATE", reason=f"last segment is a domain name ending (.{last})"
        )
    return Verdict("REFUTED")


def _class_vs_module_spelling(
    object: str,
    raw_object: str,
    evidence: list[SymbolEvidence],
    evidence_by_name: dict[str, list[SymbolEvidence]],
) -> str | None:
    """The module spelling when a class-shaped claim matches only a module.

    Symbol keys are case-folded so docs may lowercase CamelCase classes
    (``pkg.mod.parser`` for ``Parser``). The reverse is not symmetric: a
    *dotted, capitalized* last segment (``mypkg.Client``) names a class or an
    attribute, and if its exact path resolves only to a module whose own
    spelling is lowercase (``mypkg.client``), the class the doc references does
    not exist — the module is a same-named neighbour, not the claim's referent
    .

    Suppressed (stays SUPPORTED) when a non-module symbol of the same name
    exists anywhere in the tree: a shortened or re-exported class reference
    (``polars.DataFrame``, ``typer.Typer``) is legitimate. Bare claims are not
    affected — their ambiguity is handled by the last-segment branch.
    Returns the module's original-case qualified name for the hint, or ``None``.
    """
    if not raw_object or "." not in object:
        return None
    last = raw_object.rsplit(".", 1)[-1]
    if not last[:1].isupper():
        return None
    if not evidence or not all(item.kind == KIND_MODULE for item in evidence):
        return None
    base = object.rsplit(".", 1)[-1]
    if any(
        item.kind != KIND_MODULE
        for key in last_segment_candidates(base, evidence_by_name)
        for item in evidence_by_name.get(key, ())
    ):
        return None  # a class/attribute of that name exists — legitimate reference
    module_last = evidence[0].qualified_name.rsplit(".", 1)[-1]
    if module_last[:1].isupper():
        return None  # the module's own name is capitalized — same spelling family
    return evidence[0].qualified_name


def _is_cython_generated(object: str, evidence_by_name) -> bool:
    """Whether a dotted claim names a Cython/generated surface the AST
    inventory cannot enumerate.

    A ``cython_`` segment (``scipy.linalg.cython_blas``,
    ``scipy.special.cython_special``) is a build-generated interface module.
    A module prefix that exists only as ``.pyx``/``.pxd``/``.pyi`` is opaque:
    the harness parsed what it could (``def``/``cpdef``/``cdef class``,
    stub declarations) but cannot guarantee completeness. Absence in either is
    not a CLOSED-world finding.
    """
    if any("cython_" in segment for segment in object.split(".")):
        return True
    module_prefix = object.rsplit(".", 1)[0]
    items = evidence_by_name.get(module_prefix, ())
    return any(
        getattr(item, "kind", None) == KIND_MODULE
        and item.source_file.endswith(
            (".pyx", ".pxd", ".pyi", ".pyd", ".so", ".dylib", ".dll", ".rs")
        )
        for item in items
    )


# Namespaces whose members are constructed at runtime rather than statically
# defined in the tree. ``pytest.mark`` is a dynamically-built attribute surface
# (its markers are created by ``MarkGenerator``), so a ``pytest.mark.parametrize``
# claim is a real public name that the AST inventory cannot enumerate — absence
# is not conclusive.
_DYNAMIC_NAMESPACES: frozenset[str] = frozenset({"pytest.mark"})


def _is_dynamic_surface(object: str, evidence_by_name) -> bool:
    """Whether a dotted claim's module prefix is a dynamic attribute surface.

    A module with a module-level ``__getattr__`` (PEP 562) serves every missing
    attribute at runtime (``click.get_text_stream`` comes from click's module
    ``__getattr__``); a known dynamically-constructed namespace (``pytest.mark``)
    produces members without static definitions. The AST inventory cannot
    enumerate either, so absence in the prefix is not a CLOSED-world finding.
    """
    parts = object.split(".")
    for i in range(2, len(parts)):
        if ".".join(parts[:i]) in _DYNAMIC_NAMESPACES:
            return True
    module_prefix = object.rsplit(".", 1)[0]
    items = evidence_by_name.get(f"{module_prefix}.__getattr__", ())
    return any(getattr(item, "kind", None) == KIND_FUNCTION for item in items)


def _evidence_ids(items: list[SymbolEvidence]) -> tuple[str, ...]:
    return tuple(e.evidence_id for e in items)


symbol_exists_predicate = Predicate(
    name=SYMBOL_EXISTS_PREDICATE,
    world=SYMBOL_EXISTS_WORLD,
    scan=symbol_exists_scan,
    harvest=build_symbol_inventory,
    match=symbol_exists_match,
    flags=symbol_exists_flags,
    gate=symbol_exists_gate,
    world_holds=has_project_python,
)
