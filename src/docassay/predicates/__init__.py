"""Predicates: per-predicate extraction (anchor-first) and matching (§3, §4, §6).

The pipeline analyzes a repository over the registered predicate plugins. A new
predicate is a module exposing its ``scan``/``harvest``/``match`` functions and a
``Predicate`` instance, appended to ``ALL_PREDICATES`` below.
"""

from __future__ import annotations

from docassay.predicates.base import Predicate
from docassay.predicates.crossdoc import license_predicate
from docassay.predicates.dependency import dependency_predicate
from docassay.predicates.infra import (
    has_ci_workflow_predicate,
    has_dockerfile_predicate,
)
from docassay.predicates.listing import path_exists_predicate
from docassay.predicates.structure import symbol_exists_predicate

ALL_PREDICATES: tuple[Predicate, ...] = (
    dependency_predicate,
    path_exists_predicate,
    symbol_exists_predicate,
    license_predicate,
    has_dockerfile_predicate,
    has_ci_workflow_predicate,
)

__all__ = ["Predicate", "ALL_PREDICATES"]
