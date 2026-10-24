"""The surviving injection mechanics.

Extracted from the retired deterministic-operator pipeline. What remains is only
the part that is *not* circular and is shared with the LLM injector:

- :mod:`engine.grammar` — which mutation kinds exist and how each is applied on
  disk (the applier plus conflict/resource helpers);
- :mod:`engine.oracle` — the engine-free verifier that proves an injected defect
  exists on disk (``verify_without_tool``).

The retired registry (target selection), the registry-driven driver and its
samplers are archived under
the retired deterministic-operator pipeline (not shipped).
"""
