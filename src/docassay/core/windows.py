"""Context window construction.

A window is the unit around an anchor from which context markers are cut.
Sentence-level for prose, line-level for lists/code.
"""

from __future__ import annotations

import functools
import re

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_LONG_LINE_CHARS = 160
_LIST_MARKER_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_FENCE_RE = re.compile(r"^\s*(?:`{3,}|~{3,})")

# A prose line that ends in one of these is a sentence fragment that continues
# on the next physical line ("We do not", "requires Python 3.9 and", "Note:").
# Such fragments are merged with the following line so a negation split across
# a line break ("does not\nrequire NumPy") stays one window.
_CONTINUATION_TAIL_RE = re.compile(
    r"(?:[,;:—–]|[-–]\s*|\b(?:a|an|and|are|as|at|because|but|by|cannot|could|"
    r"did|do|does|for|from|if|in|is|like|may|might|must|not|of|on|or|should|"
    r"so|such|than|that|the|then|to|using|was|were|when|which|will|with|"
    r"without|would|you)\b)$",
    re.IGNORECASE,
)


_TAIL_CHARS = 32


def _ends_open(text: str) -> bool:
    """``_CONTINUATION_TAIL_RE.search(text)``, scanning only the text's tail.

    The pattern is anchored at the end and its alternatives are short, so a
    match starting inside the last ``_TAIL_CHARS`` characters (after the
    first, where a word boundary could not be judged) is a match of the full
    text. Anything else — a candidate at the tail's first character or a
    whitespace-only tail — falls back to the full search, so the result is
    always identical to it.
    """
    if len(text) <= _TAIL_CHARS:
        return bool(_CONTINUATION_TAIL_RE.search(text))
    tail = text[-_TAIL_CHARS:]
    match = _CONTINUATION_TAIL_RE.search(tail)
    if match is not None and match.start() > 0:
        return True
    if match is None and tail.strip():
        return False
    return bool(_CONTINUATION_TAIL_RE.search(text))


def _is_continuation(text: str) -> bool:
    """Whether ``text`` continues the previous sentence (starts in lowercase)."""
    return bool(text) and (text[0].islower() or text[0].isdigit() or text[0] in "`([{")


def line_at(line_map, pos: int, default: int) -> int:
    """The physical source line of the character at window offset ``pos``.

    ``line_map`` is the per-window offset→line map (``None`` for single-line
    windows, where ``default`` — the window's own line — is exact). For a merged
    multi-line window the map resolves the *anchor's* line, so provenance stays
    precise even when the window spans several physical lines.
    """
    if line_map is None:
        return default
    best = line_map[0][1]
    for offset, line_no in line_map:
        if offset <= pos:
            best = line_no
        else:
            break
    return best


def anchor_line_text(window: str, line_map, start: int) -> str:
    """The window segment that belongs to the anchor's own physical line.

    For a merged multi-line window, context markers (negation, version) are
    extracted over the whole sentence, but the claim's ``raw_context`` must
    stay the anchor's own line: gates and downgrade flags (historical,
    test-env, instructional, exemplary) scan ``raw_context``, and foreign words
    from the neighbouring line ("tested on", "requires") must not hide a real
    finding. For single-line windows this is just the window itself.
    """
    if line_map is None:
        return window
    bstart = 0
    bend: int | None = None
    for i, (offset, _line_no) in enumerate(line_map):
        if offset <= start:
            bstart = offset
            bend = line_map[i + 1][0] - 1 if i + 1 < len(line_map) else None
        else:
            break
    return window[bstart:] if bend is None else window[bstart:bend]


def _split_table_row(row: str) -> list[str]:
    body = row.strip().strip("|")
    return [cell.strip() for cell in body.split("|")]


_SEPARATOR_CELL_RE = re.compile(r"^:?-+:?$")


def _is_separator_row(row: str) -> bool:
    """Whether a table row is a Markdown ``| --- | :--: |`` separator."""
    cells = _split_table_row(row)
    return bool(cells) and all(_SEPARATOR_CELL_RE.match(c) for c in cells if c)


def _table_windows(block: list[tuple[int, str]], *, strip_code: bool):
    """A table block → ``<header> <cell>`` windows for each data row.

    A requirements table like ``| Python | 3.10+ |`` is dropped as a window
    today; pairing the column header with the data cell turns it into a claim
    window ("Python 3.10+"), so the version is extracted.
    The window carries the data row's line number for provenance.
    """
    if len(block) < 3 or not _is_separator_row(block[1][1]):
        return
    header_cells = _split_table_row(block[0][1])
    for line_no, row in block[2:]:
        cells = _split_table_row(row)
        for header, cell in zip(header_cells, cells, strict=False):
            window = f"{header} {cell}"
            if strip_code:
                window = re.sub(r"`([^`]+)`", r"\1", window)
            window = window.strip()
            if window:
                yield window, line_no, line_no, None


def _iter_windows(text: str, *, strip_code: bool):
    """Yield ``(window, line_start, line_end, line_map)`` over a document.

    ``line_start``/``line_end`` are 1-based, inclusive source-line numbers of
    the window; ``line_map`` is ``None`` for single-line windows and an
    ``(offset, line)`` map for merged multi-line windows (see ``line_at``).
    Empty lines, code fences and lone table rows are dropped as windows but
    their line numbers are still accounted for, so the span always points at
    the physical line the window came from. A long prose line split into
    sentences yields several windows that share the same span.
    """
    lines = text.splitlines()
    n = len(lines)
    i = 0
    pending: tuple[str, int, int, list[tuple[int, int]]] | None = None
    while i < n:
        line_no = i + 1
        stripped = lines[i].strip()
        i += 1
        if not stripped or _FENCE_RE.match(stripped):
            # A hard boundary ends any pending sentence fragment.
            if pending:
                yield _finalize(pending)
                pending = None
            continue
        if stripped.startswith("|"):
            if pending:
                yield _finalize(pending)
                pending = None
            block = [(line_no, stripped)]
            while i < n and lines[i].strip().startswith("|"):
                block.append((i + 1, lines[i].strip()))
                i += 1
            yield from _table_windows(block, strip_code=strip_code)
            continue
        was_list_item = bool(_LIST_MARKER_RE.match(stripped))
        window = _LIST_MARKER_RE.sub("", stripped)
        if strip_code:
            window = re.sub(r"`([^`]+)`", r"\1", window)
        window = window.strip(" *-")
        if not window:
            continue
        if len(window) > _LONG_LINE_CHARS:
            if pending:
                yield _finalize(pending)
                pending = None
            for part in _SENTENCE_SPLIT_RE.split(window):
                part = part.strip()
                if part:
                    yield part, line_no, line_no, None
            continue
        if pending is not None:
            if not was_list_item and _is_continuation(window) and _ends_open(pending[0]):
                # Merge: the new line continues the pending fragment; record the
                # boundary so an anchor's line can be resolved precisely.
                boundaries = pending[3] + [(len(pending[0]) + 1, line_no)]
                pending = (pending[0] + " " + window, pending[1], line_no, boundaries)
                continue
            yield _finalize(pending)
            pending = None
        if was_list_item or not _ends_open(window):
            yield window, line_no, line_no, None
        else:
            pending = (window, line_no, line_no, [(0, line_no)])
    if pending:
        yield _finalize(pending)


def _finalize(
    pending: tuple[str, int, int, list[tuple[int, int]]],
) -> tuple[str, int, int, tuple[tuple[int, int], ...] | None]:
    """Emit a pending window; a never-merged fragment stays line_map ``None``."""
    window, start, end, boundaries = pending
    if len(boundaries) == 1:
        return window, start, end, None
    return window, start, end, tuple(boundaries)


def iter_windows(text: str):
    """Yield ``(window, line_start, line_end, line_map)`` from a document.

    Long prose lines are split into sentences; list items, headings and code
    lines stay whole so "python 3.9 or higher" or ``pip install django==5.0``
    remain one window. Table rows and code fences are dropped unless a table
    carries a header+separator, in which case header-cell pairs are emitted. A
    sentence fragment that continues on the next line is merged into one
    multi-line window with a ``line_map`` for exact anchor provenance.
    """
    yield from _cached_windows(text, True)


def iter_windows_preserve_code(text: str):
    """Yield ``(window, line_start, line_end, line_map)`` keeping code backticks.

    The predicate-level anchor for structure claims (`` `src/foo.py` ``) needs
    the backtick boundary, so this variant skips the backtick stripping that
    ``iter_windows`` applies.
    """
    yield from _cached_windows(text, False)


@functools.lru_cache(maxsize=512)
def _cached_windows(text: str, strip_code: bool) -> tuple:
    # Every predicate cuts every document into windows; one analysis computes
    # them once per document and variant.
    return tuple(_iter_windows(text, strip_code=strip_code))


def clear_window_cache() -> None:
    """Drop cached windows (called when an analysis finishes)."""
    _cached_windows.cache_clear()
