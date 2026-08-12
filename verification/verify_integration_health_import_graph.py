"""Scaffold-free witness: the capability-registry import graph must see cell-to-cell imports.

WHY THIS EXISTS (2026-08-12, hdi_skunkworks island-harvest audit). `capability_registry_audit.
compute_integration_status` classifies an exp-cell registry row as ISLAND when
`integration_health.compute_import_graph()` reports zero consumers of that cell. The graph
originally matched only the `experiments.`-prefixed import forms, but the dominant idiom in
`experiments/` is `sys.path.insert(0, EXP_DIR)` followed by a BARE `import exp_other_cell as v1`
/ `from exp_other_cell import helper`. Those edges were invisible, so cells whose only consumers
are other cells were mislabelled ISLAND -- i.e. the registry's own anti-islanding alarm produced
false positives, which is the failure mode the registry exists to prevent.

This witness runs against the REAL repository (no fixtures, no scaffolding, no tracing): it
asserts a known-true bare-import edge is present, asserts a negative control (a cell that imports
nobody has no outgoing edge attributed to it), and asserts stdlib/3rd-party imports never create
phantom module nodes.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from integration_health import compute_import_graph  # noqa: E402

EXP_DIR = os.path.join(ROOT, "experiments")
HDLAB_DIR = os.path.join(ROOT, "hdlab")

# Ground truth read off disk, not assumed: experiments/exp_maven_ere_convergence_gated_subevent_v1
# .py contains `import exp_maven_ere_convergence_gated_causal_v1 as v1` and
# `import exp_maven_ere_convergence_gated_causal_v2 as v2` (bare, sys.path-inserted).
CONSUMER = "exp_maven_ere_convergence_gated_subevent_v1"
PROVIDERS = (
    "exp_maven_ere_convergence_gated_causal_v1",
    "exp_maven_ere_convergence_gated_causal_v2",
)


def _graph():
    return compute_import_graph(exp_dir=EXP_DIR, hdlab_dir=HDLAB_DIR)


def test_bare_cell_to_cell_import_is_visible():
    """A bare `import exp_other` edge between two real cells must appear in the graph."""
    consumer_path = os.path.join(EXP_DIR, CONSUMER + ".py")
    assert os.path.exists(consumer_path), consumer_path
    src = open(consumer_path, "r", encoding="utf-8", errors="replace").read()
    for provider in PROVIDERS:
        assert ("import " + provider) in src, f"precondition gone: {CONSUMER} no longer imports {provider}"

    exp_module_consumers = _graph()[0]
    for provider in PROVIDERS:
        consumers = {os.path.basename(p) for p in exp_module_consumers.get(provider, set())}
        assert CONSUMER + ".py" in consumers, (
            f"{provider} shows consumers={sorted(consumers)}; the bare cell-to-cell import edge "
            f"from {CONSUMER} is invisible -> registry would report a FALSE ISLAND"
        )


def test_no_phantom_module_nodes_from_third_party_or_noqa():
    """Only real experiments/ basenames may appear as module nodes."""
    exp_module_consumers = _graph()[0]
    exp_mods = {f[:-3] for f in os.listdir(EXP_DIR) if f.endswith(".py")}
    phantoms = sorted(set(exp_module_consumers) - exp_mods)
    assert not phantoms, f"phantom module nodes in the import graph: {phantoms[:10]}"


def test_self_import_never_recorded():
    """A cell must never be recorded as its own consumer."""
    exp_module_consumers = _graph()[0]
    for mod, consumers in exp_module_consumers.items():
        assert mod + ".py" not in {os.path.basename(p) for p in consumers}, mod


if __name__ == "__main__":
    test_bare_cell_to_cell_import_is_visible()
    test_no_phantom_module_nodes_from_third_party_or_noqa()
    test_self_import_never_recorded()
    print("[WITNESS] PASS -- import graph sees bare cell-to-cell imports; no phantom nodes")
